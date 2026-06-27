import base64
import json
import mimetypes
import os
import time
from pathlib import Path
from typing import Any

import requests

from .models import Document, DocumentAsset
from .storage import get_absolute_path

VISION_PROVIDER_OPENAI_COMPATIBLE = 'openai_compatible'
VISION_PROVIDER_ZHIPU = 'zhipu'
VISION_PROVIDERS = {
    VISION_PROVIDER_OPENAI_COMPATIBLE,
    VISION_PROVIDER_ZHIPU,
}
VISION_TRANSIENT_ERROR_CODES = {'1305'}
VISION_TRANSIENT_STATUS_CODES = {408, 409, 425, 429, 500, 502, 503, 504}


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
                'vision_provider': result.get('provider', ''),
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


def _call_vision_model(asset: DocumentAsset, image_path: Path, api_key: str) -> dict[str, Any]:
    provider = _vision_provider()
    base_url = _vision_base_url(provider)
    timeout = float(os.getenv('VISION_TIMEOUT_SECONDS', '60'))
    prompt = os.getenv('VISION_PROMPT', _default_vision_prompt()).strip()
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
    }
    retry_attempts = _positive_int_env('VISION_RETRY_ATTEMPTS', 2)
    retry_backoff = _positive_float_env('VISION_RETRY_BACKOFF_SECONDS', 1.0, allow_zero=True)
    model_errors: list[dict[str, Any]] = []
    last_result: dict[str, Any] | None = None

    for model in _vision_model_candidates():
        errors: list[str] = []
        attempts_used = 0
        for attempt in range(1, retry_attempts + 1):
            attempts_used = attempt
            result = _request_vision_completion(
                provider=provider,
                base_url=base_url,
                model=model,
                asset=asset,
                image_path=image_path,
                prompt=prompt,
                headers=headers,
                timeout=timeout,
            )
            last_result = result
            if result['status'] == DocumentAsset.VisionStatus.SUCCESS:
                return result
            if result['status'] == DocumentAsset.VisionStatus.SKIPPED:
                return result

            errors.append(result.get('error') or '视觉模型调用失败')
            if not result.get('retryable'):
                break
            if attempt < retry_attempts and retry_backoff > 0:
                time.sleep(retry_backoff * attempt)

        model_errors.append({
            'model': model,
            'errors': errors,
            'attempts': attempts_used,
        })
        if not last_result or not last_result.get('retryable'):
            break

    fallback_error = _format_final_vision_error(model_errors)
    return {
        'status': DocumentAsset.VisionStatus.FAILED,
        'text': '',
        'error': fallback_error,
        'model': last_result.get('model', '') if last_result else '',
        'provider': provider,
    }


def _request_vision_completion(
    *,
    provider: str,
    base_url: str,
    model: str,
    asset: DocumentAsset,
    image_path: Path,
    prompt: str,
    headers: dict[str, str],
    timeout: float,
) -> dict[str, Any]:
    payload = _vision_payload(
        provider=provider,
        model=model,
        asset=asset,
        image_path=image_path,
        prompt=prompt,
    )

    try:
        response = requests.post(
            f'{base_url}/chat/completions',
            headers=headers,
            json=payload,
            timeout=timeout,
        )
    except requests.Timeout:
        return _vision_failure(
            provider=provider,
            model=model,
            error='视觉模型请求超时，请稍后点击“重新解析”重试。',
            retryable=True,
        )
    except requests.RequestException as exc:
        return _vision_failure(
            provider=provider,
            model=model,
            error=f'视觉模型请求失败：{exc}',
            retryable=True,
        )

    if response.status_code >= 400:
        details = _response_error_details(response)
        error = _format_vision_http_error(
            provider=provider,
            status_code=response.status_code,
            error_code=details['code'],
            message=details['message'],
        )
        return _vision_failure(
            provider=provider,
            model=model,
            error=error,
            retryable=_is_retryable_vision_error(response.status_code, details['code']),
        )

    try:
        text = response.json()['choices'][0]['message']['content'].strip()
    except (KeyError, IndexError, TypeError, ValueError) as exc:
        return _vision_failure(
            provider=provider,
            model=model,
            error=f'视觉模型响应格式异常：{exc}',
            retryable=False,
        )

    if not text:
        return {'status': DocumentAsset.VisionStatus.SKIPPED, 'text': '', 'error': 'No vision text generated'}

    return {
        'status': DocumentAsset.VisionStatus.SUCCESS,
        'text': text,
        'error': '',
        'model': model,
        'provider': provider,
    }


def _vision_failure(
    *,
    provider: str,
    model: str,
    error: str,
    retryable: bool,
) -> dict[str, Any]:
    return {
        'status': DocumentAsset.VisionStatus.FAILED,
        'text': '',
        'error': error,
        'model': model,
        'provider': provider,
        'retryable': retryable,
    }


def _vision_model_candidates() -> list[str]:
    primary = os.getenv('VISION_MODEL', 'gpt-4o-mini').strip() or 'gpt-4o-mini'
    models = [primary, *_comma_separated_env('VISION_FALLBACK_MODELS')]
    candidates: list[str] = []
    for model in models:
        if model and model not in candidates:
            candidates.append(model)
    return candidates


def _comma_separated_env(name: str) -> list[str]:
    return [
        item.strip()
        for item in os.getenv(name, '').split(',')
        if item.strip()
    ]


def _positive_int_env(name: str, default: int) -> int:
    try:
        value = int(os.getenv(name, str(default)))
    except ValueError:
        return default
    return max(1, value)


def _positive_float_env(name: str, default: float, *, allow_zero: bool = False) -> float:
    try:
        value = float(os.getenv(name, str(default)))
    except ValueError:
        return default
    minimum = 0.0 if allow_zero else 0.1
    return max(minimum, value)


def _response_error_details(response: requests.Response) -> dict[str, str]:
    payload: Any = None
    try:
        payload = response.json()
    except ValueError:
        if response.text:
            try:
                payload = json.loads(response.text)
            except ValueError:
                payload = None

    if isinstance(payload, dict):
        error = payload.get('error')
        if isinstance(error, dict):
            return {
                'code': str(error.get('code') or ''),
                'message': str(error.get('message') or response.text or ''),
            }
        return {
            'code': str(payload.get('code') or ''),
            'message': str(payload.get('message') or response.text or ''),
        }

    return {'code': '', 'message': response.text or ''}


def _format_vision_http_error(
    *,
    provider: str,
    status_code: int,
    error_code: str,
    message: str,
) -> str:
    service = '智谱' if provider == VISION_PROVIDER_ZHIPU else '视觉服务'
    clean_message = _compact_error_text(message)
    if status_code in {401, 403}:
        return f'{service}鉴权失败，请检查 VISION_API_KEY、模型权限或账户额度。'
    if error_code in VISION_TRANSIENT_ERROR_CODES:
        return f'{service}返回错误 {error_code}：{clean_message or "模型当前暂时繁忙"}，请稍后点击“重新解析”重试。'
    if status_code == 429:
        return f'{service}请求过于频繁或额度受限，请稍后点击“重新解析”重试。'
    if status_code >= 500:
        return f'{service}服务暂时不可用（HTTP {status_code}），请稍后点击“重新解析”重试。'

    code_part = f'，错误 {error_code}' if error_code else ''
    message_part = f'：{clean_message}' if clean_message else ''
    return f'{service}请求失败（HTTP {status_code}{code_part}）{message_part}'


def _compact_error_text(text: str) -> str:
    return ' '.join(text.split())[:300]


def _is_retryable_vision_error(status_code: int, error_code: str) -> bool:
    return status_code in VISION_TRANSIENT_STATUS_CODES or error_code in VISION_TRANSIENT_ERROR_CODES


def _format_final_vision_error(model_errors: list[dict[str, Any]]) -> str:
    summaries = []
    for item in model_errors:
        errors = item['errors']
        if not errors:
            continue
        latest_error = errors[-1]
        attempts = item['attempts']
        attempt_text = f'（已尝试 {attempts} 次）' if attempts > 1 else ''
        summaries.append(f"{item['model']}: {latest_error}{attempt_text}")

    if not summaries:
        return '视觉模型调用失败，请稍后点击“重新解析”重试。'
    if len(summaries) == 1:
        return summaries[0]
    return f'视觉模型均不可用：{"；".join(summaries)}'


def _vision_provider() -> str:
    provider = os.getenv('VISION_PROVIDER', VISION_PROVIDER_OPENAI_COMPATIBLE).strip().lower()
    if not provider:
        return VISION_PROVIDER_OPENAI_COMPATIBLE
    if provider not in VISION_PROVIDERS:
        return VISION_PROVIDER_OPENAI_COMPATIBLE
    return provider


def _vision_base_url(provider: str) -> str:
    default_base_url = {
        VISION_PROVIDER_ZHIPU: 'https://open.bigmodel.cn/api/paas/v4',
        VISION_PROVIDER_OPENAI_COMPATIBLE: 'https://api.openai.com/v1',
    }.get(provider, 'https://api.openai.com/v1')
    configured_base_url = os.getenv('VISION_BASE_URL', '').strip()
    return (configured_base_url or default_base_url).rstrip('/')


def _vision_payload(
    provider: str,
    model: str,
    asset: DocumentAsset,
    image_path: Path,
    prompt: str,
) -> dict[str, Any]:
    image_url = _image_data_url(image_path)
    payload: dict[str, Any] = {
        'model': model,
        'messages': [
            {
                'role': 'user',
                'content': [
                    {'type': 'text', 'text': _asset_prompt(asset, prompt)},
                    {'type': 'image_url', 'image_url': {'url': image_url}},
                ],
            }
        ],
        'temperature': 0.1,
    }
    if provider == VISION_PROVIDER_ZHIPU:
        payload['messages'][0]['content'][1]['image_url']['url'] = _image_base64(image_path)
        thinking = os.getenv('VISION_THINKING', '').strip().lower()
        if thinking in {'enabled', 'disabled'}:
            payload['thinking'] = {'type': thinking}
    return payload


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
    encoded = _image_base64(image_path)
    return f'data:{mime_type};base64,{encoded}'


def _image_base64(image_path: Path) -> str:
    return base64.b64encode(image_path.read_bytes()).decode('ascii')


def _asset_context_metadata(asset: DocumentAsset) -> dict[str, Any]:
    metadata = asset.metadata or {}
    return {
        key: metadata[key]
        for key in ('source', 'page', 'alt_text', 'target', 'line')
        if key in metadata
    }


def _vision_enabled() -> bool:
    return os.getenv('VISION_ENABLED', 'false').lower() not in {'false', '0', 'no'}
