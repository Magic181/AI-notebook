from rest_framework import serializers

from .models import Notebook


class NotebookSerializer(serializers.ModelSerializer):
    document_count = serializers.SerializerMethodField()

    class Meta:
        model = Notebook
        fields = (
            'id',
            'name',
            'description',
            'is_favorite',
            'document_count',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'is_favorite', 'document_count', 'created_at', 'updated_at')

    def get_document_count(self, obj):
        return 0


class NotebookCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notebook
        fields = ('name', 'description')

    def validate_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError('名称不能为空')
        return value


class NotebookUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notebook
        fields = ('name', 'description')

    def validate_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError('名称不能为空')
        return value
