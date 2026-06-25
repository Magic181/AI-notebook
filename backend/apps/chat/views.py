import logging
import os

from django.db import transaction
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.notebooks.models import Notebook

from .models import Conversation, Message, MessageRole
from .rag import DeepSeekError, build_prompt, call_deepseek_chat, retrieve_citations
from .serializers import (
    ConversationCreateSerializer,
    ConversationSerializer,
    MessageSerializer,
    SendMessageSerializer,
)
from .web_search import WebSearchError, search_web

logger = logging.getLogger(__name__)
AI_FAILURE_MESSAGE = "回答生成失败，请稍后重试，或检查 AI 服务配置。"
WEB_SEARCH_DEGRADED_MESSAGE = "联网搜索失败，已基于本地资料回答。"
WEB_ONLY_SEARCH_DEGRADED_MESSAGE = "联网搜索失败，已基于模型通用能力回答。"


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
        conversations = notebook.conversations.all()
        return Response(ConversationSerializer(conversations, many=True).data)

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
        messages = conv.messages.all()
        return Response(MessageSerializer(messages, many=True).data)


class ConversationSendMessageView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, conversation_pk: int):
        conv = get_user_conversation(request.user, conversation_pk)
        serializer = SendMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        content = serializer.validated_data["content"].strip()
        search_mode = serializer.validated_data.get(
            "search_mode",
            SendMessageSerializer.SEARCH_MODE_LOCAL,
        )

        with transaction.atomic():
            user_msg = Message.objects.create(
                conversation=conv, role=MessageRole.USER, content=content, citations=[]
            )
            conv.save(update_fields=["updated_at"])

        citations = []
        web_results = []
        web_search_degraded = False
        try:
            top_k = int(os.getenv("RAG_TOP_K", "5"))
            max_ctx = int(os.getenv("RAG_MAX_CONTEXT_CHARS", "8000"))
            if search_mode in (
                SendMessageSerializer.SEARCH_MODE_LOCAL,
                SendMessageSerializer.SEARCH_MODE_HYBRID,
            ):
                citations = retrieve_citations(conv.notebook_id, content, top_k=top_k)
            if search_mode in (
                SendMessageSerializer.SEARCH_MODE_WEB,
                SendMessageSerializer.SEARCH_MODE_HYBRID,
            ):
                try:
                    web_results = search_web(content)
                except WebSearchError:
                    logger.warning(
                        "Web search failed for conversation %s",
                        conv.id,
                        exc_info=True,
                    )
                    web_search_degraded = True
            messages = build_prompt(
                content,
                citations,
                max_context_chars=max_ctx,
                web_results=web_results,
            )
            answer = call_deepseek_chat(messages)
            if web_search_degraded:
                degraded_message = (
                    WEB_ONLY_SEARCH_DEGRADED_MESSAGE
                    if search_mode == SendMessageSerializer.SEARCH_MODE_WEB
                    else WEB_SEARCH_DEGRADED_MESSAGE
                )
                answer = f"{degraded_message}\n\n{answer}"
        except DeepSeekError as exc:
            logger.exception("Failed to generate chat response for conversation %s", conv.id)
            answer = getattr(exc, "user_message", AI_FAILURE_MESSAGE)
        except Exception:
            logger.exception("Unexpected chat response failure for conversation %s", conv.id)
            answer = AI_FAILURE_MESSAGE

        with transaction.atomic():
            assistant_msg = Message.objects.create(
                conversation=conv,
                role=MessageRole.ASSISTANT,
                content=answer,
                citations=[
                    {
                        "source_type": "document",
                        "document_id": c.document_id,
                        "document_name": c.document_name,
                        "chunk_id": c.chunk_id,
                        "chunk_text": c.chunk_text,
                        "position": c.position,
                    }
                    for c in citations
                ]
                + [
                    {
                        "source_type": "web",
                        "title": result.title,
                        "url": result.url,
                        "content": result.content,
                        "position": result.position,
                    }
                    for result in web_results
                ],
            )
            conv.updated_at = assistant_msg.created_at
            conv.save(update_fields=["updated_at"])

        return Response(
            {
                "user_message": MessageSerializer(user_msg).data,
                "assistant_message": MessageSerializer(assistant_msg).data,
            }
        )

