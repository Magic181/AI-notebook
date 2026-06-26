from django.contrib import admin

from .models import Document, DocumentAsset, DocumentChunk


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'notebook', 'file_type', 'status', 'chunk_count', 'created_at')
    list_filter = ('status', 'file_type')
    search_fields = ('name',)


@admin.register(DocumentChunk)
class DocumentChunkAdmin(admin.ModelAdmin):
    list_display = ('id', 'document', 'position')
    search_fields = ('content',)


@admin.register(DocumentAsset)
class DocumentAssetAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'document',
        'asset_type',
        'position',
        'original_name',
        'ocr_status',
        'file_path',
    )
    list_filter = ('asset_type', 'ocr_status')
    search_fields = ('original_name', 'nearby_text', 'ocr_text')
