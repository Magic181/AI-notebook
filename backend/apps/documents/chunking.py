import re
from typing import Any


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[dict[str, Any]]:
    text = _normalize_text(text)
    paragraphs = [p.strip() for p in re.split(r'\n\s*\n', text) if p.strip()]
    return chunk_blocks(
        [
            {'content': paragraph, 'metadata': {'source_type': 'paragraph', 'block_index': index}}
            for index, paragraph in enumerate(paragraphs)
        ],
        chunk_size=chunk_size,
        overlap=overlap,
    )


def chunk_blocks(
    blocks: list[dict[str, Any]],
    chunk_size: int = 500,
    overlap: int = 50,
) -> list[dict[str, Any]]:
    chunks: list[dict[str, Any]] = []
    current = ''
    current_metadata: list[dict[str, Any]] = []

    def flush_current() -> None:
        nonlocal current, current_metadata
        if not current.strip():
            return
        chunks.append({
            'content': current.strip(),
            'metadata': _merge_metadata(current_metadata),
        })
        current = ''
        current_metadata = []

    for block in blocks:
        content = _normalize_text(block.get('content') or '')
        if not content:
            continue

        metadata = block.get('metadata') or {}
        source_type = metadata.get('source_type') or block.get('source_type') or 'text'
        if source_type == 'table':
            flush_current()
            chunks.extend(_chunk_single_block(content, metadata, chunk_size, overlap))
            continue

        if len(content) > chunk_size:
            flush_current()
            chunks.extend(_chunk_single_block(content, metadata, chunk_size, overlap))
            continue

        candidate = f'{current}\n\n{content}'.strip() if current else content
        if len(candidate) <= chunk_size:
            current = candidate
            current_metadata.append(metadata)
            continue

        flush_current()
        current = content
        current_metadata = [metadata]

    flush_current()

    return [
        {'content': chunk['content'], 'metadata': chunk['metadata'], 'position': index}
        for index, chunk in enumerate(chunks)
        if chunk['content']
    ]


def _chunk_single_block(
    content: str,
    metadata: dict[str, Any],
    chunk_size: int,
    overlap: int,
) -> list[dict[str, Any]]:
    if len(content) <= chunk_size:
        return [{'content': content, 'metadata': metadata}]
    return [
        {
            'content': item,
            'metadata': {**metadata, 'part_index': index},
        }
        for index, item in enumerate(_split_long_paragraph(content, chunk_size, overlap))
    ]


def _normalize_text(text: str) -> str:
    text = re.sub(r'\n{3,}', '\n\n', text.strip())
    return text


def _merge_metadata(items: list[dict[str, Any]]) -> dict[str, Any]:
    if not items:
        return {'source_type': 'text'}
    if len(items) == 1:
        return items[0]

    source_types = []
    block_indexes = []
    for item in items:
        source_type = item.get('source_type')
        block_index = item.get('block_index')
        if source_type and source_type not in source_types:
            source_types.append(source_type)
        if block_index is not None:
            block_indexes.append(block_index)
    return {
        'source_type': source_types[0] if len(source_types) == 1 else 'mixed',
        'source_types': source_types,
        'block_indexes': block_indexes,
    }


def _split_long_paragraph(text: str, chunk_size: int, overlap: int) -> list[str]:
    result: list[str] = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        result.append(text[start:end].strip())
        if end >= len(text):
            break
        start = max(end - overlap, start + 1)
    return [item for item in result if item]
