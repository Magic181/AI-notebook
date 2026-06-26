import base64
import mimetypes
import os
from pathlib import Path
from typing import Any

import requests

from .models import Document, DocumentAsset
from .storage import get_absolute_path


def build_vision_blocks(document: Document) -> list[dict[str, Any]]:
    blocks: list[dict[str, Any]] = []
    for asset in document.assets.filter(asset_type=DocumentAsset.AssetType.IMAGE).order_by('position'):
        result = run_asset_vision(asset)
        _save_vision_result(asset, result)
        if result['status'] != DocumentAsset.VisionStatus.SUCCESS:
            continue

        blocks.append({
            'content': _format_vision_content(asset, result['text']),
            'source_type': 'image_caption',
            'metadata': {
                'source_type': 'image_caption',
                'file_type': document.file_type,
                'parser_version': 1,
                'asset_id': asset.id,
                'asset_position': asset.position,
                'asset_name': asset.original_name,
                'vision_model': result.get('model', ''),
                **_asset_context_metadata(asset),
            },
        })
    return blocks


def run_asset_vision(asset: DocumentAsset) -> dict[str, str]:
    if not _vision_enabled():
        return {'status': DocumentAsset.VisionStatus.SKIPPED, 'text': '', 'error': 'Vision disabled'}
    if not asset.file_path:
        return {'status': DocumentAsset.VisionStatus.SKIPPED, 'text': '', 'error': 'No local asset file'}

    api_key = os.getenv('VISION_API_KEY', '').strip()
    if not api_key:
        return {'status': DocumentAsset.VisionStatus.SKIPPED, 'text': '', 'error': 'VISION_API_KEY not configured'}

    image_path = get_absolute_path(asset.file_path)
    if not image_path.exists():
        return {'status': DocumentAsset.VisionStatus.SKIPPED, 'text': '', 'error': 'Asset file missing'}

    return _call_vision_model(asset, image_path, api_key)


def _call_vision_model(asset: DocumentAsset, image_path: Path, api_key: str) -> dict[str, str]:
    base_url = os.getenv('VISION_BASE_URL', 'https://api.openai.com/v1').rstrip('/')
    model = os.getenv('VISION_MODEL', 'gpt-4o-mini').strip() or 'gpt-4o-mini'
    timeout = float(os.getenv('VISION_TIMEOUT_SECONDS', '60'))
    prompt = os.getenv('VISION_PROMPT', _default_vision_prompt()).strip()

    data_url = _image_data_url(image_path)
    payload = {
        'model': model,
        'messages': [
            {
                'role': 'user',
                'content': [
                    {'type': 'text', 'text': _asset_prompt(asset, prompt)},
                    {'type': 'image_url', 'image_url': {'url': data_url}},
                ],
            }
        ],
        'temperature': 0.1,
    }
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
    }

    try:
        response = requests.post(
            f'{base_url}/chat/completions',
            headers=headers,
            json=payload,
            timeout=timeout,
        )
    except requests.RequestException as exc:
        return {'status': DocumentAsset.VisionStatus.FAILED, 'text': '', 'error': str(exc)}

    if response.status_code >= 400:
        return {
            'status': DocumentAsset.VisionStatus.FAILED,
            'text': '',
            'error': response.text[:500] if response.text else f'HTTP {response.status_code}',
        }

    try:
        text = response.json()['choices'][0]['message']['content'].strip()
    except (KeyError, IndexError, TypeError, ValueError) as exc:
        return {'status': DocumentAsset.VisionStatus.FAILED, 'text': '', 'error': str(exc)}

    if not text:
        return {'status': DocumentAsset.VisionStatus.SKIPPED, 'text': '', 'error': 'No vision text generated'}

    return {
        'status': DocumentAsset.VisionStatus.SUCCESS,
        'text': text,
        'error': '',
        'model': model,
    }


def _save_vision_result(asset: DocumentAsset, result: dict[str, str]) -> None:
    asset.vision_status = result['status']
    asset.vision_text = result.get('text', '')
    asset.vision_error = result.get('error', '')
    asset.save(update_fields=['vision_status', 'vision_text', 'vision_error'])


def _format_vision_content(asset: DocumentAsset, text: str) -> str:
    parts = [
        f'[图片视觉描述 #{asset.position + 1}]',
        f'文件：{asset.original_name}',
    ]
    if asset.nearby_text:
        parts.append(f'附近文字：{asset.nearby_text}')
    parts.append(f'视觉描述：\n{text}')
    return '\n'.join(parts)


def _asset_prompt(asset: DocumentAsset, base_prompt: str) -> str:
    context = []
    if asset.nearby_text:
        context.append(f'图片附近文字：{asset.nearby_text}')
    if asset.ocr_text:
        context.append(f'OCR 文本：{asset.ocr_text}')
    context_text = '\n'.join(context)
    return f'{base_prompt}\n\n{context_text}'.strip()


def _default_vision_prompt() -> str:
    return (
        '请用中文描述这张图片对文档理解有用的信息。'
        '如果是流程图、甘特图、架构图、截图或表格图，请概括其中的结构、步骤、关系、阶段或关键结论。'
        '不要编造看不清的细节；如果图片内容不清楚，请说明不清楚。'
    )


def _image_data_url(image_path: Path) -> str:
    mime_type = mimetypes.guess_type(image_path.name)[0] or 'application/octet-stream'
    encoded = base64.b64encode(image_path.read_bytes()).decode('ascii')
    return f'data:{mime_type};base64,{encoded}'


def _asset_context_metadata(asset: DocumentAsset) -> dict[str, Any]:
    metadata = asset.metadata or {}
    return {
        key: metadata[key]
        for key in ('source', 'page', 'alt_text', 'target', 'line')
        if key in metadata
    }


def _vision_enabled() -> bool:
    return os.getenv('VISION_ENABLED', 'false').lower() not in {'false', '0', 'no'}
