from celery import shared_task
from django.db import transaction

from .assets import clear_document_assets, replace_document_assets
from .chunking import chunk_blocks
from .models import Document, DocumentChunk, DocumentStatus
from .ocr import build_ocr_blocks
from .parsers import ParseError, parse_file_blocks
from .storage import get_absolute_path


@shared_task
def parse_document_task(document_id: int) -> None:
    try:
        document = Document.objects.select_related('notebook').get(pk=document_id)
    except Document.DoesNotExist:
        return

    document.status = DocumentStatus.PARSING
    document.error_message = ''
    document.save(update_fields=['status', 'error_message', 'updated_at'])

    try:
        file_path = get_absolute_path(document.file_path)
        if not file_path.exists():
            raise ParseError('文件不存在')

        blocks = parse_file_blocks(file_path, document.file_type)
        chunks = chunk_blocks(blocks)
        if not chunks:
            raise ParseError('文档内容为空')

        with transaction.atomic():
            document.chunks.all().delete()
            DocumentChunk.objects.bulk_create([
                DocumentChunk(
                    document=document,
                    content=chunk['content'],
                    metadata=chunk['metadata'],
                    position=chunk['position'],
                )
                for chunk in chunks
            ])
            replace_document_assets(document, file_path, blocks)
            ocr_chunks = chunk_blocks(build_ocr_blocks(document))
            if ocr_chunks:
                start_position = len(chunks)
                DocumentChunk.objects.bulk_create([
                    DocumentChunk(
                        document=document,
                        content=chunk['content'],
                        metadata=chunk['metadata'],
                        position=start_position + index,
                    )
                    for index, chunk in enumerate(ocr_chunks)
                ])
            document.chunk_count = len(chunks) + len(ocr_chunks)
            document.status = DocumentStatus.COMPLETED
            document.save(update_fields=['chunk_count', 'status', 'updated_at'])
    except Exception as exc:
        clear_document_assets(document)
        document.status = DocumentStatus.FAILED
        document.error_message = str(exc)
        document.chunk_count = 0
        document.save(update_fields=['status', 'error_message', 'chunk_count', 'updated_at'])
