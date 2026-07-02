import json
import logging

from django.conf import settings
from django.db import transaction
from django.http import StreamingHttpResponse
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.listing import limited_list_response
from apps.core.throttling import ChatSendRateThrottle
from apps.notebooks.models import Notebook

from .models import Conversation, Message, MessageRole
from .serializers import (
    ConversationCreateSerializer,
    ConversationSerializer,
    ConversationUpdateSerializer,
    MessageSerializer,
    SendMessageSerializer,
)
from .rag import DeepSeekError, stream_deepseek_chat, strip_inline_source_markers
from .services import (
    AI_FAILURE_MESSAGE,
    build_citation_payload,
    generate_assistant_draft,
    prepare_assistant_context,
)

logger = logging.getLogger(__name__)


def get_user_notebook(user, notebook_id: int) -> Notebook:
    try:
        return Notebook.objects.get(pk=notebook_id, user=user)
    except Notebook.DoesNotExist as exc:
        raise NotFound("笔记本不存在") from exc


def get_user_conversation(user, conversation_id: int) -> Conversation:
    try:
        return Conversation.objects.select_related("notebook").get(
            pk=conversation_id, notebook__user=user
        )
    except Conversation.DoesNotExist as exc:
        raise NotFound("会话不存在") from exc


class NotebookConversationListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, notebook_pk: int):
        notebook = get_user_notebook(request.user, notebook_pk)
        queryset = notebook.conversations.all()
        total = queryset.count()
        conversations = queryset[:settings.MAX_LIST_RESULTS]
        return limited_list_response(
            ConversationSerializer(conversations, many=True).data,
            total=total,
        )

    def post(self, request, notebook_pk: int):
        notebook = get_user_notebook(request.user, notebook_pk)
        serializer = ConversationCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        title = (serializer.validated_data.get("title") or "").strip()
        conv = Conversation.objects.create(notebook=notebook, title=title)
        return Response(ConversationSerializer(conv).data, status=status.HTTP_201_CREATED)


class ConversationMessageListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, conversation_pk: int):
        conv = get_user_conversation(request.user, conversation_pk)
        # Messages default-order oldest-first; cap by keeping the most recent
        # MAX_LIST_RESULTS, then restore chronological order for the response.
        queryset = conv.messages.all()
        total = queryset.count()
        messages = list(queryset.order_by('-created_at')[:settings.MAX_LIST_RESULTS])
        messages.reverse()
        return limited_list_response(
            MessageSerializer(messages, many=True).data,
            total=total,
        )


class ConversationDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, conversation_pk: int):
        conv = get_user_conversation(request.user, conversation_pk)
        serializer = ConversationUpdateSerializer(conv, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(ConversationSerializer(conv).data)

    def delete(self, request, conversation_pk: int):
        conv = get_user_conversation(request.user, conversation_pk)
        conv.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ConversationSendMessageView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [ChatSendRateThrottle]

    def post(self, request, conversation_pk: int):
        conv = get_user_conversation(request.user, conversation_pk)
        serializer = SendMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        content = serializer.validated_data["content"].strip()
        search_mode = serializer.validated_data.get(
            "search_mode",
            SendMessageSerializer.SEARCH_MODE_LOCAL,
        )
        history_messages = list(conv.messages.order_by("-id")[:6])
        history_messages.reverse()

        with transaction.atomic():
            user_msg = Message.objects.create(
                conversation=conv, role=MessageRole.USER, content=content, citations=[]
            )
            conv.save(update_fields=["updated_at"])

        assistant_draft = generate_assistant_draft(
            conv,
            content,
            search_mode,
            history_messages=history_messages,
        )

        with transaction.atomic():
            assistant_msg = Message.objects.create(
                conversation=conv,
                role=MessageRole.ASSISTANT,
                content=assistant_draft.content,
                citations=build_citation_payload(
                    assistant_draft.citations,
                    assistant_draft.web_results,
                ),
            )
            conv.updated_at = assistant_msg.created_at
            conv.save(update_fields=["updated_at"])

        return Response(
            {
                "user_message": MessageSerializer(user_msg).data,
                "assistant_message": MessageSerializer(assistant_msg).data,
            }
        )


class ConversationSendMessageStreamView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [ChatSendRateThrottle]

    def post(self, request, conversation_pk: int):
        conv = get_user_conversation(request.user, conversation_pk)
        serializer = SendMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        content = serializer.validated_data["content"].strip()
        search_mode = serializer.validated_data.get(
            "search_mode",
            SendMessageSerializer.SEARCH_MODE_LOCAL,
        )
        history_messages = list(conv.messages.order_by("-id")[:6])
        history_messages.reverse()

        with transaction.atomic():
            user_msg = Message.objects.create(
                conversation=conv, role=MessageRole.USER, content=content, citations=[]
            )
            conv.save(update_fields=["updated_at"])

        response = StreamingHttpResponse(
            self._stream_assistant_response(
                conv.id,
                content,
                search_mode,
                history_messages,
                user_msg,
            ),
            content_type="text/event-stream; charset=utf-8",
        )
        response["Cache-Control"] = "no-cache"
        response["X-Accel-Buffering"] = "no"
        return response

    def _stream_assistant_response(
        self,
        conversation_id: int,
        content: str,
        search_mode: str,
        history_messages: list,
        user_msg: Message,
    ):
        context = None
        answer_parts: list[str] = []
        raw_answer_parts: list[str] = []
        visible_answer = ''

        yield _sse_event("user_message", MessageSerializer(user_msg).data)

        try:
            conv = Conversation.objects.select_related("notebook").get(pk=conversation_id)
            context = prepare_assistant_context(
                conversation=conv,
                content=content,
                search_mode=search_mode,
                history_messages=history_messages,
            )

            if context.degraded_message:
                degraded_content = f"{context.degraded_message}\n\n"
                answer_parts.append(degraded_content)
                yield _sse_event("delta", {"content": degraded_content})

            for chunk in stream_deepseek_chat(context.messages):
                raw_answer_parts.append(chunk)
                next_visible_answer = strip_inline_source_markers("".join(raw_answer_parts), strip_partial=True)
                if not next_visible_answer.startswith(visible_answer):
                    visible_answer = next_visible_answer
                    continue
                delta = next_visible_answer[len(visible_answer):]
                if delta:
                    answer_parts.append(delta)
                    visible_answer = next_visible_answer
                    yield _sse_event("delta", {"content": delta})

            assistant_content = strip_inline_source_markers("".join(raw_answer_parts)).strip() or AI_FAILURE_MESSAGE
        except DeepSeekError as exc:
            logger.exception(
                "Failed to stream chat response for conversation %s",
                conversation_id,
            )
            assistant_content = _stream_failure_content(answer_parts, exc)
            if not answer_parts:
                yield _sse_event("delta", {"content": assistant_content})
            yield _sse_event("error", {"message": getattr(exc, "user_message", AI_FAILURE_MESSAGE)})
        except Exception:
            logger.exception(
                "Unexpected streaming chat response failure for conversation %s",
                conversation_id,
            )
            assistant_content = _stream_failure_content(answer_parts)
            if not answer_parts:
                yield _sse_event("delta", {"content": assistant_content})
            yield _sse_event("error", {"message": AI_FAILURE_MESSAGE})

        citations = build_citation_payload(
            context.citations if context else [],
            context.web_results if context else [],
        )
        with transaction.atomic():
            conv = Conversation.objects.get(pk=conversation_id)
            assistant_msg = Message.objects.create(
                conversation=conv,
                role=MessageRole.ASSISTANT,
                content=assistant_content,
                citations=citations,
            )
            conv.updated_at = assistant_msg.created_at
            conv.save(update_fields=["updated_at"])

        yield _sse_event("assistant_message", MessageSerializer(assistant_msg).data)
        yield _sse_event("done", {})


def _sse_event(event: str, data: dict) -> str:
    payload = json.dumps(data, ensure_ascii=False)
    return f"event: {event}\ndata: {payload}\n\n"


def _stream_failure_content(
    answer_parts: list[str],
    exc: DeepSeekError | None = None,
) -> str:
    failure_message = getattr(exc, "user_message", AI_FAILURE_MESSAGE)
    partial_answer = "".join(answer_parts).strip()
    if not partial_answer:
        return failure_message
    return f"{partial_answer}\n\n{failure_message}"
