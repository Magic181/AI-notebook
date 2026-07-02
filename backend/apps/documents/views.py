import logging
from pathlib import Path

from django.conf import settings
from django.db import transaction
from rest_framework import status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.listing import limited_list_response
from apps.notebooks.models import Notebook

from .models import Document, DocumentStatus
from .serializers import DocumentSerializer
from .storage import delete_file, save_uploaded_file
from .tasks import parse_document_task

ALLOWED_EXTENSIONS = {'.txt', '.md', '.markdown', '.pdf', '.docx'}
logger = logging.getLogger(__name__)


def normalize_file_type(filename: str) -> str:
    ext = Path(filename).suffix.lower()
    if ext == '.markdown':
        return 'md'
    return ext.lstrip('.')


def validate_uploaded_files(files) -> None:
    max_files = settings.MAX_UPLOAD_FILES_PER_REQUEST
    if len(files) > max_files:
        raise ValidationError({
            'files': f'单次最多上传 {max_files} 个文件',
        })

    max_size = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    for uploaded in files:
        ext = Path(uploaded.name).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise ValidationError({
                'files': f'不支持的文件格式: {uploaded.name}（支持 TXT/MD/PDF/DOCX）',
            })
        if uploaded.size > max_size:
            raise ValidationError({
                'files': f'文件过大: {uploaded.name}（最大 {settings.MAX_UPLOAD_SIZE_MB}MB）',
            })


def cleanup_saved_files(paths: list[str]) -> None:
    for path in paths:
        delete_file(path)


def cleanup_document_files(paths: list[str]) -> None:
    for path in paths:
        if not path:
            continue
        try:
            delete_file(path)
        except OSError:
            logger.warning("Failed to delete document file %s", path, exc_info=True)


def enqueue_parse_task(document_id: int) -> None:
    try:
        parse_document_task.delay(document_id)
    except Exception as exc:
        Document.objects.filter(pk=document_id).update(
            status=DocumentStatus.FAILED,
            error_message=f'解析任务入队失败: {exc}',
            chunk_count=0,
        )


def get_user_notebook(user, notebook_id: int) -> Notebook:
    try:
        return Notebook.objects.get(pk=notebook_id, user=user)
    except Notebook.DoesNotExist as exc:
        raise NotFound('笔记本不存在') from exc


def get_user_document(user, document_id: int) -> Document:
    try:
        return Document.objects.select_related('notebook').get(
            pk=document_id,
            notebook__user=user,
        )
    except Document.DoesNotExist as exc:
        raise NotFound('文档不存在') from exc


class NotebookDocumentListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, notebook_pk: int):
        notebook = get_user_notebook(request.user, notebook_pk)
        queryset = notebook.documents.prefetch_related('assets', 'chunks').all()
        total = queryset.count()
        documents = queryset[:settings.MAX_LIST_RESULTS]
        return limited_list_response(
            DocumentSerializer(documents, many=True).data,
            total=total,
        )

    def post(self, request, notebook_pk: int):
        notebook = get_user_notebook(request.user, notebook_pk)
        files = request.FILES.getlist('files')
        if not files:
            single = request.FILES.get('file')
            files = [single] if single else []

        if not files:
            raise ValidationError({'files': '请选择要上传的文件'})

        validate_uploaded_files(files)

        saved_paths = []
        created = []

        try:
            with transaction.atomic():
                for uploaded in files:
                    file_type = normalize_file_type(uploaded.name)
                    relative_path, size = save_uploaded_file(
                        request.user.id,
                        notebook.id,
                        uploaded,
                    )
                    saved_paths.append(relative_path)
                    document = Document.objects.create(
                        notebook=notebook,
                        name=uploaded.name,
                        file_path=relative_path,
                        file_size=size,
                        file_type=file_type,
                        status=DocumentStatus.UPLOADING,
                    )
                    transaction.on_commit(
                        lambda document_id=document.id: enqueue_parse_task(document_id),
                    )
                    created.append(document)
        except Exception:
            cleanup_saved_files(saved_paths)
            raise

        return Response(
            DocumentSerializer(created, many=True).data,
            status=status.HTTP_201_CREATED,
        )


class DocumentDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk: int):
        document = get_user_document(request.user, pk)
        return Response(DocumentSerializer(document).data)

    def delete(self, request, pk: int):
        document = get_user_document(request.user, pk)
        file_paths = [
            document.file_path,
            *document.assets.exclude(file_path='').values_list('file_path', flat=True),
        ]
        with transaction.atomic():
            document.delete()
            transaction.on_commit(lambda: cleanup_document_files(file_paths))
        return Response(status=status.HTTP_204_NO_CONTENT)


class DocumentReparseView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk: int):
        document = get_user_document(request.user, pk)
        if document.status in {DocumentStatus.UPLOADING, DocumentStatus.PARSING}:
            raise ValidationError({'status': '文档正在处理中，请完成后再重新解析'})

        document.status = DocumentStatus.PARSING
        document.error_message = ''
        document.chunk_count = 0
        document.save(update_fields=['status', 'error_message', 'chunk_count', 'updated_at'])
        enqueue_parse_task(document.id)
        document.refresh_from_db()
        return Response(DocumentSerializer(document).data, status=status.HTTP_202_ACCEPTED)
