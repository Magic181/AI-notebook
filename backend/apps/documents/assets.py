import re
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from django.conf import settings

from .models import Document, DocumentAsset
from .storage import delete_file


@dataclass(frozen=True)
class ExtractedAsset:
    asset_type: str
    original_name: str
    position: int
    nearby_text: str = ''
    metadata: dict[str, Any] | None = None
    data: bytes | None = None
    extension: str = ''
    source_path: Path | None = None


def replace_document_assets(
    document: Document,
    file_path: Path,
    blocks: list[dict[str, Any]],
) -> int:
    clear_document_assets(document)
    assets = extract_assets(file_path, document.file_type, blocks)
    if not assets:
        return 0

    records = []
    for asset in assets:
        relative_path = _persist_asset(document, asset)
        records.append(
            DocumentAsset(
                document=document,
                asset_type=asset.asset_type,
                file_path=relative_path,
                original_name=asset.original_name,
                position=asset.position,
                nearby_text=asset.nearby_text,
                metadata=asset.metadata or {},
            )
        )
    DocumentAsset.objects.bulk_create(records)
    return len(records)


def extract_assets(
    file_path: Path,
    file_type: str,
    blocks: list[dict[str, Any]],
) -> list[ExtractedAsset]:
    if file_type == 'docx':
        return _extract_docx_images(file_path, blocks)
    if file_type == 'pdf':
        return _extract_pdf_images(file_path, blocks)
    if file_type == 'md':
        return _extract_markdown_images(file_path)
    return []


def _extract_docx_images(file_path: Path, blocks: list[dict[str, Any]]) -> list[ExtractedAsset]:
    if not zipfile.is_zipfile(file_path):
        return []

    nearby_text = _nearby_text_from_blocks(blocks)
    assets = []
    with zipfile.ZipFile(file_path) as archive:
        names = sorted(
            name for name in archive.namelist()
            if name.startswith('word/media/') and not name.endswith('/')
        )
        for index, name in enumerate(names):
            data = archive.read(name)
            original_name = Path(name).name
            assets.append(
                ExtractedAsset(
                    asset_type=DocumentAsset.AssetType.IMAGE,
                    original_name=original_name,
                    position=index,
                    nearby_text=nearby_text,
                    metadata={
                        'source': 'docx',
                        'archive_path': name,
                        'file_type': 'docx',
                    },
                    data=data,
                    extension=Path(original_name).suffix,
                )
            )
    return assets


def _extract_pdf_images(file_path: Path, blocks: list[dict[str, Any]]) -> list[ExtractedAsset]:
    from pypdf import PdfReader

    assets = []
    try:
        reader = PdfReader(str(file_path))
    except Exception:
        return []

    position = 0
    for page_index, page in enumerate(reader.pages, start=1):
        for image in getattr(page, 'images', []) or []:
            data = getattr(image, 'data', None)
            if not data:
                continue
            original_name = getattr(image, 'name', '') or f'page-{page_index}-image-{position + 1}'
            assets.append(
                ExtractedAsset(
                    asset_type=DocumentAsset.AssetType.IMAGE,
                    original_name=original_name,
                    position=position,
                    nearby_text=_nearby_text_for_page(blocks, page_index),
                    metadata={
                        'source': 'pdf',
                        'file_type': 'pdf',
                        'page': page_index,
                    },
                    data=data,
                    extension=Path(original_name).suffix,
                )
            )
            position += 1
    return assets


def _extract_markdown_images(file_path: Path) -> list[ExtractedAsset]:
    text = _read_text_file(file_path)
    lines = text.splitlines()
    assets = []
    pattern = re.compile(r'!\[([^\]]*)\]\(([^)]+)\)')

    for line_index, line in enumerate(lines):
        for match in pattern.finditer(line):
            alt_text = match.group(1).strip()
            target = match.group(2).strip().strip('"\'')
            source_path = _resolve_markdown_image_path(file_path, target)
            assets.append(
                ExtractedAsset(
                    asset_type=DocumentAsset.AssetType.IMAGE,
                    original_name=Path(target).name or target,
                    position=len(assets),
                    nearby_text=_nearby_text_for_line(lines, line_index),
                    metadata={
                        'source': 'markdown',
                        'file_type': 'md',
                        'alt_text': alt_text,
                        'target': target,
                        'line': line_index + 1,
                        'is_local': source_path is not None,
                    },
                    source_path=source_path,
                    extension=Path(target).suffix,
                )
            )
    return assets


def _persist_asset(document: Document, asset: ExtractedAsset) -> str:
    data = asset.data
    if data is None and asset.source_path and asset.source_path.exists():
        data = asset.source_path.read_bytes()
    if data is None:
        return ''

    extension = asset.extension or Path(asset.original_name).suffix or '.bin'
    filename = f'{asset.position:04d}{extension.lower()}'
    relative_path = Path('assets') / str(document.notebook.user_id) / str(document.notebook_id) / str(document.id) / filename
    absolute_path = Path(settings.MEDIA_ROOT) / relative_path
    absolute_path.parent.mkdir(parents=True, exist_ok=True)
    absolute_path.write_bytes(data)
    return str(relative_path)


def clear_document_assets(document: Document) -> None:
    for asset in document.assets.all():
        if asset.file_path:
            delete_file(asset.file_path)
    document.assets.all().delete()


def _nearby_text_from_blocks(blocks: list[dict[str, Any]], limit: int = 500) -> str:
    text_blocks = [
        block.get('content', '').strip()
        for block in blocks
        if (block.get('content') or '').strip()
        and (block.get('metadata') or {}).get('source_type') in {'heading', 'paragraph'}
    ]
    return '\n'.join(text_blocks[:3])[:limit]


def _nearby_text_for_page(blocks: list[dict[str, Any]], page: int, limit: int = 500) -> str:
    for block in blocks:
        metadata = block.get('metadata') or {}
        if metadata.get('page') == page:
            return (block.get('content') or '')[:limit]
    return ''


def _nearby_text_for_line(lines: list[str], line_index: int, limit: int = 500) -> str:
    start = max(0, line_index - 2)
    end = min(len(lines), line_index + 3)
    nearby = [line.strip() for line in lines[start:end] if line.strip()]
    return '\n'.join(nearby)[:limit]


def _resolve_markdown_image_path(file_path: Path, target: str) -> Path | None:
    if re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:', target):
        return None
    candidate = (file_path.parent / target).resolve()
    try:
        candidate.relative_to(file_path.parent.resolve())
    except ValueError:
        return None
    return candidate if candidate.exists() else None


def _read_text_file(file_path: Path) -> str:
    for encoding in ('utf-8', 'utf-8-sig', 'gbk'):
        try:
            return file_path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    return ''
