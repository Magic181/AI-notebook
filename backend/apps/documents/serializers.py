from rest_framework import serializers

from .models import Document, DocumentAsset


class DocumentSerializer(serializers.ModelSerializer):
    asset_count = serializers.SerializerMethodField()
    ocr_count = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = (
            'id',
            'notebook_id',
            'name',
            'file_type',
            'file_size',
            'status',
            'chunk_count',
            'asset_count',
            'ocr_count',
            'error_message',
            'created_at',
            'updated_at',
        )
        read_only_fields = fields

    def get_asset_count(self, obj):
        return obj.assets.count()

    def get_ocr_count(self, obj):
        return obj.assets.filter(ocr_status=DocumentAsset.OCRStatus.SUCCESS).count()


class DocumentUploadSerializer(serializers.Serializer):
    files = serializers.ListField(
        child=serializers.FileField(),
        allow_empty=False,
        write_only=True,
    )
