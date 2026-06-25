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
    SEARCH_MODE_LOCAL = 'local'
    SEARCH_MODE_WEB = 'web'
    SEARCH_MODE_HYBRID = 'hybrid'
    SEARCH_MODE_CHOICES = (
        (SEARCH_MODE_LOCAL, '本地资料'),
        (SEARCH_MODE_WEB, '联网搜索'),
        (SEARCH_MODE_HYBRID, '混合搜索'),
    )

    content = serializers.CharField(allow_blank=False, trim_whitespace=True)
    web_search = serializers.BooleanField(required=False, default=False)
    search_mode = serializers.ChoiceField(
        choices=SEARCH_MODE_CHOICES,
        required=False,
        default=SEARCH_MODE_LOCAL,
    )

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if attrs.get('web_search') and attrs.get('search_mode') == self.SEARCH_MODE_LOCAL:
            attrs['search_mode'] = self.SEARCH_MODE_HYBRID
        return attrs

