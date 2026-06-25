from rest_framework import serializers

from .models import Conversation, Message


class ConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        fields = ('id', 'notebook_id', 'title', 'created_at', 'updated_at')
        read_only_fields = fields


class ConversationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        fields = ('title',)


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ('id', 'conversation_id', 'role', 'content', 'citations', 'created_at')
        read_only_fields = fields


class SendMessageSerializer(serializers.Serializer):
    content = serializers.CharField(allow_blank=False, trim_whitespace=True)
    web_search = serializers.BooleanField(required=False, default=False)

