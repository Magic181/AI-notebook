import logging
import os
from dataclasses import dataclass

from .models import Conversation
from .models import MessageRole
from .rag import Citation, DeepSeekError, build_prompt, call_deepseek_chat, retrieve_citations
from .search_modes import SEARCH_MODE_WEB, uses_local_retrieval, uses_web_search
from .web_search import WebResult, WebSearchError, search_web

logger = logging.getLogger(__name__)

AI_FAILURE_MESSAGE = "回答生成失败，请稍后重试，或检查 AI 服务配置。"
WEB_SEARCH_DEGRADED_MESSAGE = "联网搜索失败，已基于本地资料回答。"
WEB_ONLY_SEARCH_DEGRADED_MESSAGE = "联网搜索失败，已基于模型通用能力回答。"


@dataclass(frozen=True)
class AssistantDraft:
    content: str
    citations: list[Citation]
    web_results: list[WebResult]


def generate_assistant_draft(
    conversation: Conversation,
    content: str,
    search_mode: str,
    history_messages: list | None = None,
) -> AssistantDraft:
    citations: list[Citation] = []
    web_results: list[WebResult] = []
    web_search_degraded = False

    try:
        top_k = int(os.getenv("RAG_TOP_K", "5"))
        max_ctx = int(os.getenv("RAG_MAX_CONTEXT_CHARS", "8000"))
        history_messages = history_messages or []
        local_query = _build_local_query(content, history_messages)

        if uses_local_retrieval(search_mode):
            citations = retrieve_citations(conversation.notebook_id, local_query, top_k=top_k)

        if uses_web_search(search_mode):
            try:
                web_results = search_web(content)
            except WebSearchError:
                logger.warning(
                    "Web search failed for conversation %s",
                    conversation.id,
                    exc_info=True,
                )
                web_search_degraded = True

        messages = build_prompt(
            content,
            citations,
            max_context_chars=max_ctx,
            web_results=web_results,
            history=_build_prompt_history(history_messages),
        )
        answer = call_deepseek_chat(messages)
        if web_search_degraded:
            answer = f"{_web_search_degraded_message(search_mode)}\n\n{answer}"
    except DeepSeekError as exc:
        logger.exception("Failed to generate chat response for conversation %s", conversation.id)
        answer = getattr(exc, "user_message", AI_FAILURE_MESSAGE)
    except Exception:
        logger.exception("Unexpected chat response failure for conversation %s", conversation.id)
        answer = AI_FAILURE_MESSAGE

    return AssistantDraft(content=answer, citations=citations, web_results=web_results)


def build_citation_payload(
    citations: list[Citation],
    web_results: list[WebResult],
) -> list[dict]:
    return [
        {
            "source_type": "document",
            "document_id": citation.document_id,
            "document_name": citation.document_name,
            "chunk_id": citation.chunk_id,
            "chunk_text": citation.chunk_text,
            "position": citation.position,
            "document_source_type": citation.source_type,
            "metadata": citation.metadata,
        }
        for citation in citations
    ] + [
        {
            "source_type": "web",
            "title": result.title,
            "url": result.url,
            "content": result.content,
            "position": result.position,
        }
        for result in web_results
    ]


def _web_search_degraded_message(search_mode: str) -> str:
    if search_mode == SEARCH_MODE_WEB:
        return WEB_ONLY_SEARCH_DEGRADED_MESSAGE
    return WEB_SEARCH_DEGRADED_MESSAGE


def _build_local_query(content: str, history_messages: list) -> str:
    user_context = [
        msg.content.strip()
        for msg in history_messages
        if msg.role == MessageRole.USER and msg.content.strip()
    ]
    return "\n".join([*user_context[-3:], content])


def _build_prompt_history(history_messages: list) -> list[dict[str, str]]:
    return [
        {"role": msg.role, "content": msg.content}
        for msg in history_messages[-6:]
        if msg.role in {MessageRole.USER, MessageRole.ASSISTANT}
    ]
