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


def parse_file(file_path: Path, file_type: str) -> str:
    blocks = parse_file_blocks(file_path, file_type)
    return '\n\n'.join(block['content'] for block in blocks if block.get('content'))


def parse_file_blocks(file_path: Path, file_type: str) -> list[ParsedBlock]:
    parsers = {
        'txt': _parse_text_blocks,
        'md': _parse_text_blocks,
        'pdf': _parse_pdf_blocks,
        'docx': _parse_docx_blocks,
    }
    parser = parsers.get(file_type)
    if not parser:
        raise ParseError(f'不支持的文件类型: .{file_type}')
    return parser(file_path)


def _parse_text_blocks(file_path: Path) -> list[ParsedBlock]:
    for encoding in ('utf-8', 'utf-8-sig', 'gbk'):
        try:
            text = file_path.read_text(encoding=encoding)
            break
        except UnicodeDecodeError:
            continue
    else:
        raise ParseError('无法识别文本编码')

    blocks = [
        _block(content=paragraph, source_type='paragraph', block_index=index)
        for index, paragraph in enumerate(_split_paragraphs(text))
    ]
    if not blocks:
        raise ParseError('文档内容为空')
    return blocks


def _parse_pdf_blocks(file_path: Path) -> list[ParsedBlock]:
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
                    page=page_index,
                )
            )
    if not blocks:
        raise ParseError('PDF 中未提取到文本内容')
    return blocks


def _parse_docx_blocks(file_path: Path) -> list[ParsedBlock]:
    doc = DocxDocument(str(file_path))
    blocks: list[ParsedBlock] = []
    table_index = 0

    for item in _iter_docx_blocks(doc):
        if isinstance(item, Paragraph):
            text = item.text.strip()
            if not text:
                continue
            blocks.append(
                _block(
                    content=text,
                    source_type='paragraph',
                    block_index=len(blocks),
                    style=item.style.name if item.style else '',
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


def _split_paragraphs(text: str) -> list[str]:
    return [part.strip() for part in text.split('\n\n') if part.strip()]


def _normalize_cell_text(text: str) -> str:
    return ' '.join(part.strip() for part in text.splitlines() if part.strip())


def _block(content: str, source_type: str, block_index: int, **metadata) -> ParsedBlock:
    return {
        'content': content.strip(),
        'source_type': source_type,
        'metadata': {
            'source_type': source_type,
            'block_index': block_index,
            **{key: value for key, value in metadata.items() if value not in ('', None)},
        },
    }
