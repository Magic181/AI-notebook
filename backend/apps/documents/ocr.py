import os
import shutil
import subprocess
from pathlib import Path
from typing import Any

from .models import Document, DocumentAsset
from .storage import get_absolute_path


def build_ocr_blocks(document: Document) -> list[dict[str, Any]]:
    blocks: list[dict[str, Any]] = []
    for asset in document.assets.filter(asset_type=DocumentAsset.AssetType.IMAGE).order_by('position'):
        result = run_asset_ocr(asset)
        _save_ocr_result(asset, result)
        if result['status'] != DocumentAsset.OCRStatus.SUCCESS:
            continue

        blocks.append({
            'content': _format_ocr_content(asset, result['text']),
            'source_type': 'image_ocr',
            'metadata': {
                'source_type': 'image_ocr',
                'file_type': document.file_type,
                'parser_version': 1,
                'asset_id': asset.id,
                'asset_position': asset.position,
                'asset_name': asset.original_name,
                'ocr_engine': result.get('engine', ''),
                **_asset_context_metadata(asset),
            },
        })
    return blocks


def run_asset_ocr(asset: DocumentAsset) -> dict[str, str]:
    if not _ocr_enabled():
        return {'status': DocumentAsset.OCRStatus.SKIPPED, 'text': '', 'error': 'OCR disabled'}
    if not asset.file_path:
        return {'status': DocumentAsset.OCRStatus.SKIPPED, 'text': '', 'error': 'No local asset file'}

    image_path = get_absolute_path(asset.file_path)
    if not image_path.exists():
        return {'status': DocumentAsset.OCRStatus.SKIPPED, 'text': '', 'error': 'Asset file missing'}

    command = _tesseract_command()
    if not command:
        return {
            'status': DocumentAsset.OCRStatus.SKIPPED,
            'text': '',
            'error': 'Tesseract command not found',
        }

    return _run_tesseract(command, image_path)


def _run_tesseract(command: str, image_path: Path) -> dict[str, str]:
    timeout = float(os.getenv('OCR_TIMEOUT_SECONDS', '30'))
    language = os.getenv('OCR_LANG', 'chi_sim+eng').strip() or 'eng'
    args = [command, str(image_path), 'stdout', '-l', language]
    try:
        completed = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return {'status': DocumentAsset.OCRStatus.FAILED, 'text': '', 'error': 'OCR timeout'}
    except OSError as exc:
        return {'status': DocumentAsset.OCRStatus.FAILED, 'text': '', 'error': str(exc)}

    if completed.returncode != 0:
        return {
            'status': DocumentAsset.OCRStatus.FAILED,
            'text': '',
            'error': (completed.stderr or 'OCR command failed')[:500],
        }

    text = _normalize_ocr_text(completed.stdout)
    if not text:
        return {'status': DocumentAsset.OCRStatus.SKIPPED, 'text': '', 'error': 'No OCR text extracted'}

    return {
        'status': DocumentAsset.OCRStatus.SUCCESS,
        'text': text,
        'error': '',
        'engine': 'tesseract',
    }


def _save_ocr_result(asset: DocumentAsset, result: dict[str, str]) -> None:
    asset.ocr_status = result['status']
    asset.ocr_text = result.get('text', '')
    asset.ocr_error = result.get('error', '')
    asset.save(update_fields=['ocr_status', 'ocr_text', 'ocr_error'])


def _format_ocr_content(asset: DocumentAsset, text: str) -> str:
    parts = [
        f'[图片 OCR #{asset.position + 1}]',
        f'文件：{asset.original_name}',
    ]
    if asset.nearby_text:
        parts.append(f'附近文字：{asset.nearby_text}')
    parts.append(f'OCR 文本：\n{text}')
    return '\n'.join(parts)


def _asset_context_metadata(asset: DocumentAsset) -> dict[str, Any]:
    metadata = asset.metadata or {}
    return {
        key: metadata[key]
        for key in ('source', 'page', 'alt_text', 'target', 'line')
        if key in metadata
    }


def _ocr_enabled() -> bool:
    return os.getenv('OCR_ENABLED', 'true').lower() not in {'false', '0', 'no'}


def _tesseract_command() -> str:
    configured = os.getenv('OCR_TESSERACT_CMD', 'tesseract').strip()
    if not configured:
        return ''
    return configured if shutil.which(configured) else ''


def _normalize_ocr_text(text: str) -> str:
    lines = [line.strip() for line in text.splitlines()]
    return '\n'.join(line for line in lines if line).strip()
