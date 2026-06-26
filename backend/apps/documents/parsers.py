from pathlib import Path
from typing import Any

from docx import Document as DocxDocument
from docx.oxml.table import CT_Tbl
from docx.oxml.text.paragraph import CT_P
from docx.table import Table
from docx.text.paragraph import Paragraph
from pypdf import PdfReader


class ParseError(Exception):
    pass


ParsedBlock = dict[str, Any]
PARSER_VERSION = 1


def parse_file(file_path: Path, file_type: str) -> str:
    blocks = parse_file_blocks(file_path, file_type)
    return '\n\n'.join(block['content'] for block in blocks if block.get('content'))


def parse_file_blocks(file_path: Path, file_type: str) -> list[ParsedBlock]:
    parsers = {
        'txt': _parse_text_blocks,
        'md': _parse_markdown_blocks,
        'pdf': _parse_pdf_blocks,
        'docx': _parse_docx_blocks,
    }
    parser = parsers.get(file_type)
    if not parser:
        raise ParseError(f'不支持的文件类型: .{file_type}')
    return parser(file_path, file_type)


def _parse_text_blocks(file_path: Path, file_type: str) -> list[ParsedBlock]:
    text = _read_text_file(file_path)

    blocks = [
        _block(
            content=paragraph,
            source_type='paragraph',
            block_index=index,
            file_type=file_type,
        )
        for index, paragraph in enumerate(_split_paragraphs(text))
    ]
    if not blocks:
        raise ParseError('文档内容为空')
    return blocks


def _parse_markdown_blocks(file_path: Path, file_type: str) -> list[ParsedBlock]:
    text = _read_text_file(file_path)
    blocks: list[ParsedBlock] = []
    current_lines: list[str] = []
    in_code_block = False
    code_lines: list[str] = []
    code_language = ''
    table_lines: list[str] = []

    def flush_paragraph() -> None:
        nonlocal current_lines
        content = '\n'.join(current_lines).strip()
        if content:
            blocks.append(
                _block(
                    content=content,
                    source_type='paragraph',
                    block_index=len(blocks),
                    file_type=file_type,
                )
            )
        current_lines = []

    def flush_code() -> None:
        nonlocal code_lines, code_language
        content = '\n'.join(code_lines).strip()
        if content:
            blocks.append(
                _block(
                    content=content,
                    source_type='code',
                    block_index=len(blocks),
                    file_type=file_type,
                    language=code_language,
                )
            )
        code_lines = []
        code_language = ''

    def flush_table() -> None:
        nonlocal table_lines
        if table_lines:
            blocks.append(
                _block(
                    content='\n'.join(table_lines).strip(),
                    source_type='table',
                    block_index=len(blocks),
                    file_type=file_type,
                    table_format='markdown',
                    row_count=len(table_lines),
                )
            )
        table_lines = []

    for raw_line in text.splitlines():
        line = raw_line.rstrip()

        if line.strip().startswith('```'):
            if in_code_block:
                flush_code()
                in_code_block = False
            else:
                flush_paragraph()
                flush_table()
                in_code_block = True
                code_language = line.strip()[3:].strip()
            continue

        if in_code_block:
            code_lines.append(line)
            continue

        heading_level = _markdown_heading_level(line)
        if heading_level:
            flush_paragraph()
            flush_table()
            blocks.append(
                _block(
                    content=line.lstrip('#').strip(),
                    source_type='heading',
                    block_index=len(blocks),
                    file_type=file_type,
                    heading_level=heading_level,
                )
            )
            continue

        if _is_markdown_table_line(line):
            flush_paragraph()
            table_lines.append(line.strip())
            continue

        flush_table()
        if not line.strip():
            flush_paragraph()
            continue
        current_lines.append(line)

    if in_code_block:
        flush_code()
    flush_table()
    flush_paragraph()

    if not blocks:
        raise ParseError('文档内容为空')
    return blocks


def _parse_pdf_blocks(file_path: Path, file_type: str) -> list[ParsedBlock]:
    reader = PdfReader(str(file_path))
    blocks = []
    for page_index, page in enumerate(reader.pages, start=1):
        text = (page.extract_text() or '').strip()
        if text:
            blocks.append(
                _block(
                    content=f'[第{page_index}页]\n{text}',
                    source_type='page',
                    block_index=len(blocks),
                    file_type=file_type,
                    page=page_index,
                )
            )
    if not blocks:
        raise ParseError('PDF 中未提取到文本内容')
    return blocks


def _parse_docx_blocks(file_path: Path, file_type: str) -> list[ParsedBlock]:
    doc = DocxDocument(str(file_path))
    blocks: list[ParsedBlock] = []
    table_index = 0

    for item in _iter_docx_blocks(doc):
        if isinstance(item, Paragraph):
            text = item.text.strip()
            if not text:
                continue
            style_name = item.style.name if item.style else ''
            heading_level = _docx_heading_level(style_name)
            source_type = 'heading' if heading_level else 'paragraph'
            metadata = {'heading_level': heading_level} if heading_level else {}
            blocks.append(
                _block(
                    content=text,
                    source_type=source_type,
                    block_index=len(blocks),
                    file_type=file_type,
                    style=style_name,
                    **metadata,
                )
            )
            continue

        table_text, row_count, col_count = _format_docx_table(item)
        if not table_text:
            continue
        table_index += 1
        blocks.append(
            _block(
                content=f'[表格 {table_index}]\n{table_text}',
                source_type='table',
                block_index=len(blocks),
                file_type=file_type,
                table_index=table_index,
                row_count=row_count,
                col_count=col_count,
            )
        )

    if not blocks:
        raise ParseError('DOCX 中未提取到文本内容')
    return blocks


def _iter_docx_blocks(doc):
    for child in doc.element.body.iterchildren():
        if isinstance(child, CT_P):
            yield Paragraph(child, doc)
        elif isinstance(child, CT_Tbl):
            yield Table(child, doc)


def _format_docx_table(table: Table) -> tuple[str, int, int]:
    rows: list[str] = []
    col_count = 0
    for row_index, row in enumerate(table.rows, start=1):
        cells = [_normalize_cell_text(cell.text) for cell in row.cells]
        if not any(cells):
            continue
        col_count = max(col_count, len(cells))
        rows.append(f'行 {row_index}: ' + ' | '.join(cells))
    return '\n'.join(rows), len(rows), col_count


def _read_text_file(file_path: Path) -> str:
    for encoding in ('utf-8', 'utf-8-sig', 'gbk'):
        try:
            return file_path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    raise ParseError('无法识别文本编码')


def _split_paragraphs(text: str) -> list[str]:
    return [part.strip() for part in text.split('\n\n') if part.strip()]


def _markdown_heading_level(line: str) -> int | None:
    stripped = line.strip()
    if not stripped.startswith('#'):
        return None
    marker = stripped.split(' ', 1)[0]
    if set(marker) == {'#'} and 1 <= len(marker) <= 6:
        return len(marker)
    return None


def _is_markdown_table_line(line: str) -> bool:
    stripped = line.strip()
    return stripped.startswith('|') and stripped.endswith('|') and stripped.count('|') >= 2


def _docx_heading_level(style_name: str) -> int | None:
    normalized = style_name.lower()
    if normalized.startswith('heading '):
        value = normalized.removeprefix('heading ').strip()
        return int(value) if value.isdigit() else None
    if style_name.startswith('标题 '):
        value = style_name.removeprefix('标题 ').strip()
        return int(value) if value.isdigit() else None
    return None


def _normalize_cell_text(text: str) -> str:
    return ' '.join(part.strip() for part in text.splitlines() if part.strip())


def _block(
    content: str,
    source_type: str,
    block_index: int,
    file_type: str,
    **metadata,
) -> ParsedBlock:
    return {
        'content': content.strip(),
        'source_type': source_type,
        'metadata': {
            'source_type': source_type,
            'block_index': block_index,
            'file_type': file_type,
            'parser_version': PARSER_VERSION,
            **{key: value for key, value in metadata.items() if value not in ('', None)},
        },
    }
