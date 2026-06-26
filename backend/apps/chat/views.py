from django.db import transaction
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.notebooks.models import Notebook

from .models import Conversation, Message, MessageRole
from .serializers import (
    ConversationCreateSerializer,
    ConversationSerializer,
    MessageSerializer,
    SendMessageSerializer,
)
from .services import build_citation_payload, generate_assistant_draft


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


class ConversationDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, conversation_pk: int):
        conv = get_user_conversation(request.user, conversation_pk)
        conv.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


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
