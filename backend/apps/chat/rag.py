import os
import re
import time
from dataclasses import dataclass
from typing import Any

import requests
from requests import exceptions as request_exceptions
from django.db.models import Q

from apps.documents.models import DocumentChunk, DocumentStatus

from .web_search import WebResult


@dataclass(frozen=True)
class Citation:
    document_id: int
    document_name: str
    chunk_id: int
    chunk_text: str
    position: int
    source_type: str
    metadata: dict[str, Any]


@dataclass(frozen=True)
class QueryIntent:
    source_boosts: dict[str, int]
    fallback_source_types: tuple[str, ...]


@dataclass(frozen=True)
class ScoredChunk:
    chunk: DocumentChunk
    score: int
    reason: str
    evidence_key: tuple[Any, ...]


class DeepSeekError(RuntimeError):
    user_message = "AI 服务暂时不可用，请稍后重试。"


class DeepSeekConfigError(DeepSeekError):
    user_message = "AI 服务配置不完整，请检查 DeepSeek API Key。"


class DeepSeekAuthError(DeepSeekError):
    user_message = "AI 服务认证失败，请检查 DeepSeek API Key。"


class DeepSeekRequestError(DeepSeekError):
    user_message = "AI 请求参数无效，请检查模型配置。"


QUERY_STOP_TERMS = {
    '一下',
    '这个',
    '这些',
    '这份',
    '这篇',
    '里面',
    '内容',
    '请问',
    '请你',
    '帮我',
    '根据',
    '基于',
    '总结',
    '概括',
    '归纳',
    '整理',
}

BROAD_CONTEXT_TERMS = {
    '总结',
    '概括',
    '归纳',
    '摘要',
    '梳理',
    '整理',
    '全文',
    '文档',
    '资料',
    '文件',
    '上传',
    '读取',
    '读到',
    '报告',
    '论文',
    'notebook',
    'summarize',
    'summary',
    'overview',
}

SOURCE_INTENT_TERMS = {
    'image': (
        '图片',
        '图像',
        '截图',
        '配图',
        '照片',
        '流程图',
        '架构图',
        '图表',
        '图里',
        '图中',
        '看图',
        'image',
        'picture',
        'screenshot',
        'diagram',
        'chart',
    ),
    'table': (
        '表格',
        '表',
        '清单',
        '字段',
        '列',
        '行',
        '数据',
        '统计',
        'table',
        'sheet',
        'column',
        'row',
        'dataset',
    ),
    'code': (
        '代码',
        '函数',
        '接口',
        '脚本',
        '类',
        '方法',
        '实现',
        '报错',
        'code',
        'function',
        'class',
        'api',
        'script',
        'error',
    ),
    'heading': (
        '标题',
        '章节',
        '目录',
        '小节',
        '结构',
        'heading',
        'section',
        'outline',
    ),
}

SOURCE_TYPE_BOOSTS = {
    'image_caption': {'image': 14},
    'image_ocr': {'image': 12},
    'table': {'table': 14},
    'code': {'code': 14},
    'heading': {'heading': 8, 'code': 2},
    'paragraph': {'code': 1, 'heading': 1},
    'page': {'image': 1, 'table': 1, 'code': 1, 'heading': 1},
}


def _tokenize(query: str) -> list[str]:
    query = query.strip().lower()
    if not query:
        return []
    tokens = re.split(r'[\s,，.。;；:：!?！？()\[\]{}"“”\'`]+', query)
    terms: list[str] = []
    for token in tokens:
        if len(token) < 2:
            continue
        terms.extend(_expand_search_terms(token))
    return _unique_terms(terms)[:12]


def _expand_search_terms(token: str) -> list[str]:
    if not re.search(r'[\u4e00-\u9fff]', token):
        return [] if token in QUERY_STOP_TERMS else [token]

    cleaned = token
    for term in QUERY_STOP_TERMS:
        cleaned = cleaned.replace(term, ' ')

    terms: list[str] = []
    for segment in re.findall(r'[\u4e00-\u9fffA-Za-z0-9]+', cleaned):
        if len(segment) < 2:
            continue
        if segment not in QUERY_STOP_TERMS:
            terms.append(segment)
        if len(segment) > 4 and re.search(r'[\u4e00-\u9fff]', segment):
            terms.extend(
                segment[index:index + 2]
                for index in range(0, len(segment) - 1)
            )
    return terms


def _unique_terms(terms: list[str]) -> list[str]:
    seen: set[str] = set()
    unique: list[str] = []
    for term in terms:
        if term in QUERY_STOP_TERMS or term in seen:
            continue
        seen.add(term)
        unique.append(term)
    return unique


def _is_broad_context_query(query: str) -> bool:
    lowered = query.lower()
    return any(term in lowered for term in BROAD_CONTEXT_TERMS)


def _is_document_availability_query(query: str) -> bool:
    lowered = query.lower()
    direct_terms = ('能读到', '读得到', '读取到', '看得到', '识别到')
    if any(term in lowered for term in direct_terms):
        return True
    has_upload_subject = any(term in lowered for term in ('上传', '文件', '文档', '资料'))
    has_question_signal = any(term in lowered for term in ('能', '吗', '有没有', '是否'))
    has_read_signal = any(term in lowered for term in ('读', '看', '识别'))
    return has_upload_subject and has_question_signal and has_read_signal


def _detect_query_intent(query: str) -> QueryIntent:
    lowered = query.lower()
    matched_intents = {
        intent
        for intent, terms in SOURCE_INTENT_TERMS.items()
        if any(term in lowered for term in terms)
    }
    if not matched_intents:
        return QueryIntent(source_boosts={}, fallback_source_types=())

    source_boosts: dict[str, int] = {}
    for source_type, boosts in SOURCE_TYPE_BOOSTS.items():
        score = sum(boost for intent, boost in boosts.items() if intent in matched_intents)
        if score:
            source_boosts[source_type] = score

    fallback_source_types = tuple(
        source_type
        for source_type, _ in sorted(
            source_boosts.items(),
            key=lambda item: item[1],
            reverse=True,
        )
    )
    return QueryIntent(
        source_boosts=source_boosts,
        fallback_source_types=fallback_source_types,
    )


def retrieve_citations(notebook_id: int, query: str, top_k: int = 5) -> list[Citation]:
    tokens = _tokenize(query)
    intent = _detect_query_intent(query)
    is_broad_context_query = _is_broad_context_query(query)
    use_broad_ranking = (
        is_broad_context_query
        and not intent.fallback_source_types
        and _is_document_availability_query(query)
    )
    base_qs = DocumentChunk.objects.select_related('document').filter(
        document__notebook_id=notebook_id,
        document__status=DocumentStatus.COMPLETED,
    )
    candidate_limit = max(top_k * 8, top_k)

    chunks: list[DocumentChunk] = []
    if tokens:
        token_q = Q()
        for t in tokens:
            token_q |= Q(content__icontains=t)
        chunks.extend(base_qs.filter(token_q).order_by('-id')[:candidate_limit])
    if intent.fallback_source_types:
        chunks.extend(
            base_qs.filter(metadata__source_type__in=intent.fallback_source_types)
            .order_by('-id')[:candidate_limit]
        )
    if use_broad_ranking:
        chunks.extend(base_qs.order_by('-document__created_at', 'position')[:candidate_limit])

    chunks = _deduplicate_chunks(chunks)
    if not chunks and is_broad_context_query:
        chunks = list(base_qs.order_by('-document__created_at', 'position')[:top_k])
        use_broad_ranking = True

    scored_chunks = _score_chunks(
        chunks=chunks,
        tokens=tokens,
        intent=intent,
        use_broad_ranking=use_broad_ranking,
    )
    scored_chunks = _select_diverse_chunks(scored_chunks, top_k=top_k)

    citations: list[Citation] = []
    for item in scored_chunks:
        c = item.chunk
        doc = c.document
        metadata = {
            **(c.metadata or {}),
            'retrieval_score': item.score,
            'retrieval_reason': item.reason,
        }
        citations.append(
            Citation(
                document_id=doc.id,
                document_name=doc.name,
                chunk_id=c.id,
                chunk_text=c.content[:500],
                position=c.position,
                source_type=(c.metadata or {}).get('source_type', 'text'),
                metadata=metadata,
            )
        )
    return citations


def _score_chunks(
    chunks: list[DocumentChunk],
    tokens: list[str],
    intent: QueryIntent,
    use_broad_ranking: bool,
) -> list[ScoredChunk]:
    scored: list[ScoredChunk] = []
    for chunk in chunks:
        metadata = chunk.metadata or {}
        source_type = metadata.get('source_type', 'text')
        text = (chunk.content or '').lower()
        token_weight = 1 if use_broad_ranking else 4
        token_hits = sum(text.count(t) for t in tokens) if tokens else 0
        token_score = token_hits * token_weight
        source_score = intent.source_boosts.get(source_type, 0)
        broad_score = _broad_context_score(chunk) if use_broad_ranking else 0
        score = token_score + source_score + broad_score
        if score <= 0:
            continue
        scored.append(
            ScoredChunk(
                chunk=chunk,
                score=score,
                reason=_retrieval_reason(token_hits, source_score, broad_score),
                evidence_key=_evidence_key(chunk),
            )
        )
    scored.sort(key=lambda item: (item.score, -item.chunk.id), reverse=True)
    return scored


def _select_diverse_chunks(scored_chunks: list[ScoredChunk], top_k: int) -> list[ScoredChunk]:
    selected: list[ScoredChunk] = []
    selected_keys: set[tuple[Any, ...]] = set()

    for item in scored_chunks:
        if item.evidence_key in selected_keys:
            continue
        selected.append(item)
        selected_keys.add(item.evidence_key)
        if len(selected) >= top_k:
            return selected

    if len(selected) >= top_k:
        return selected

    selected_ids = {item.chunk.id for item in selected}
    for item in scored_chunks:
        if item.chunk.id in selected_ids:
            continue
        selected.append(item)
        selected_ids.add(item.chunk.id)
        if len(selected) >= top_k:
            break
    return selected


def _retrieval_reason(token_hits: int, source_score: int, broad_score: int) -> str:
    reasons = []
    if token_hits:
        reasons.append('keyword_match')
    if source_score:
        reasons.append('source_intent')
    if broad_score:
        reasons.append('document_context')
    return '+'.join(reasons) if reasons else 'unknown'


def _evidence_key(chunk: DocumentChunk) -> tuple[Any, ...]:
    metadata = chunk.metadata or {}
    source_type = metadata.get('source_type', 'text')
    document_id = chunk.document_id

    if source_type in {'image_ocr', 'image_caption'}:
        asset_id = metadata.get('asset_id')
        if asset_id is not None:
            return (document_id, 'image', asset_id)
        asset_position = metadata.get('asset_position')
        if asset_position is not None:
            return (document_id, 'image', asset_position)

    if source_type == 'table':
        table_index = metadata.get('table_index')
        if table_index is not None:
            return (document_id, 'table', table_index)

    page = metadata.get('page')
    if page is not None:
        return (document_id, source_type, page, chunk.position // 3)

    return (document_id, source_type, chunk.position // 3)


def _deduplicate_chunks(chunks: list[DocumentChunk]) -> list[DocumentChunk]:
    seen: set[int] = set()
    unique: list[DocumentChunk] = []
    for chunk in chunks:
        if chunk.id in seen:
            continue
        seen.add(chunk.id)
        unique.append(chunk)
    return unique


def _broad_context_score(chunk: DocumentChunk) -> int:
    position = chunk.position or 0
    return max(0, 8 - min(position, 8))


def build_prompt(
    query: str,
    citations: list[Citation],
    max_context_chars: int = 8000,
    web_results: list[WebResult] | None = None,
    history: list[dict[str, str]] | None = None,
) -> list[dict[str, Any]]:
    context_blocks: list[str] = []
    remaining = max_context_chars
    for idx, c in enumerate(citations, start=1):
        source_label = _source_label(c.source_type)
        block = (
            f"[{idx}] 文档：{c.document_name}（chunk#{c.position}，{source_label}）\n"
            f"{c.chunk_text}"
        ).strip()
        if len(block) > remaining:
            block = block[:remaining]
        if not block:
            break
        context_blocks.append(block)
        remaining -= len(block) + 2
        if remaining <= 0:
            break

    web_results = web_results or []
    for idx, result in enumerate(web_results, start=1):
        block = (
            f"[W{idx}] 网页：{result.title}\n"
            f"链接：{result.url}\n"
            f"{result.content}"
        ).strip()
        if len(block) > remaining:
            block = block[:remaining]
        if not block:
            break
        context_blocks.append(block)
        remaining -= len(block) + 2
        if remaining <= 0:
            break

    system = (
        "你是 AI Notebook 的资料协作助手，语气自然、主动、专业。\n"
        "回答规则：\n"
        "- 先直接回答用户的问题，再补充依据和限制；不要一上来要求用户重新提供资料。\n"
        "- 只要资料片段不为空，就表示已经读取到 Notebook 的可解析内容，禁止说“没有读取到上传内容”。\n"
        "- 对资料型问题，优先基于资料片段回答，并引用片段编号，如 [1][2]。\n"
        "- 如果片段只覆盖部分内容，要明确说“基于当前检索到的片段”，并给出可推断结论。\n"
        "- 如果用户问图片、流程图、截图或图表，而资料中没有图片/OCR/视觉描述，只能说明当前只能看到文档文字、表格或图片附近文字，不能看见图片像素本身；然后继续基于已读文字分析。\n"
        "- 若提供了网页搜索结果，可以结合网页内容回答，并引用网页编号，如 [W1][W2]。\n"
        "- 对问候、助手能力、模型身份、产品使用方式等通用问题，可以直接自然回答。\n"
        "- 回答要像可用的产品助手：具体、少兜圈子、少模板话。\n"
    )

    context = "\n\n".join(context_blocks) if context_blocks else ""
    source_summary = _source_summary(citations, web_results)
    if context:
        user = f"用户问题：{query}\n\n资料状态：{source_summary}\n\n资料片段：\n{context}"
    else:
        user = f"用户问题：{query}\n\n资料状态：未检索到可用资料片段。\n\n资料片段：无"

    messages = [{"role": "system", "content": system}]
    for item in history or []:
        role = item.get("role")
        content = (item.get("content") or "").strip()
        if role not in {"user", "assistant"} or not content:
            continue
        messages.append({"role": role, "content": content[:1000]})
    messages.append({"role": "user", "content": user})
    return messages


def _source_label(source_type: str) -> str:
    labels = {
        'paragraph': '正文段落',
        'heading': '标题',
        'page': '页面文本',
        'table': '表格',
        'code': '代码块',
        'image_ocr': '图片 OCR',
        'image_caption': '图片描述',
        'mixed': '混合文本',
        'text': '文本',
    }
    return labels.get(source_type, source_type or '文本')


def _source_summary(citations: list[Citation], web_results: list[WebResult]) -> str:
    parts = []
    if citations:
        source_counts: dict[str, int] = {}
        for citation in citations:
            source_counts[citation.source_type] = source_counts.get(citation.source_type, 0) + 1
        detail = '、'.join(
            f"{_source_label(source_type)} {count} 个"
            for source_type, count in source_counts.items()
        )
        parts.append(f"已检索到 Notebook 片段 {len(citations)} 个（{detail}）")
    if web_results:
        parts.append(f"已检索到网页结果 {len(web_results)} 个")
    return '；'.join(parts) if parts else '未检索到可用资料片段'


def call_deepseek_chat(messages: list[dict[str, Any]]) -> str:
    api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
    if not api_key:
        raise DeepSeekConfigError("DEEPSEEK_API_KEY 未配置")

    base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1").rstrip("/")
    model = os.getenv("DEEPSEEK_MODEL", "deepseek-v4-flash")
    retries = int(os.getenv("DEEPSEEK_MAX_RETRIES", "2"))
    backoff = float(os.getenv("DEEPSEEK_RETRY_BACKOFF_SECONDS", "0.2"))
    timeout = float(os.getenv("DEEPSEEK_TIMEOUT_SECONDS", "60"))

    data = {
        "model": model,
        "messages": messages,
        "temperature": 0.2,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    resp = _post_with_retries(
        f"{base_url}/chat/completions",
        headers=headers,
        json=data,
        timeout=timeout,
        retries=retries,
        backoff=backoff,
    )
    data = resp.json()
    return data["choices"][0]["message"]["content"]


def _post_with_retries(
    url: str,
    headers: dict[str, str],
    json: dict[str, Any],
    timeout: float,
    retries: int,
    backoff: float,
) -> requests.Response:
    last_error: Exception | None = None
    attempts = max(1, retries + 1)

    for attempt in range(attempts):
        try:
            response = requests.post(
                url,
                headers=headers,
                json=json,
                timeout=timeout,
            )
            _raise_for_deepseek_status(response)
            return response
        except (DeepSeekAuthError, DeepSeekRequestError):
            raise
        except (
            request_exceptions.Timeout,
            request_exceptions.ConnectionError,
            request_exceptions.ChunkedEncodingError,
            DeepSeekError,
        ) as exc:
            last_error = exc
            if attempt >= attempts - 1:
                break
            if backoff > 0:
                time.sleep(backoff * (attempt + 1))

    raise DeepSeekError(str(last_error or "DeepSeek request failed"))


def _raise_for_deepseek_status(response: requests.Response) -> None:
    status_code = response.status_code
    if status_code < 400:
        return
    if status_code in (401, 403):
        raise DeepSeekAuthError(_safe_error_text(response))
    if status_code in (400, 404):
        raise DeepSeekRequestError(_safe_error_text(response))
    if status_code == 429 or status_code >= 500:
        raise DeepSeekError(_safe_error_text(response))
    raise DeepSeekRequestError(_safe_error_text(response))


def _safe_error_text(response: requests.Response) -> str:
    return response.text[:500] if response.text else f"HTTP {response.status_code}"

