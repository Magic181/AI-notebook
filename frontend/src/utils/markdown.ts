export function markdownToHtml(source: string) {
  const lines = source.replace(/\r\n/g, '\n').split('\n')
  const html: string[] = []
  let paragraph: string[] = []
  let listType: 'ol' | 'ul' | null = null
  let codeFence: string[] | null = null
  let codeLanguage = ''

  const closeParagraph = () => {
    if (!paragraph.length) return
    html.push(`<p>${inlineMarkdown(paragraph.join(' '))}</p>`)
    paragraph = []
  }

  let orderedItemIndex = 0

  const closeList = () => {
    if (!listType) return
    html.push(`</${listType}>`)
    listType = null
  }

  const openList = (type: 'ol' | 'ul') => {
    if (listType === type) return
    closeList()
    if (type === 'ol') {
      orderedItemIndex = 0
      html.push('<ol class="ai-action-list">')
    } else {
      html.push('<ul>')
    }
    listType = type
  }

  let index = 0
  while (index < lines.length) {
    const line = lines[index]
    const trimmed = line.trim()

    if (trimmed.startsWith('```')) {
      closeParagraph()
      closeList()
      if (codeFence) {
        const languageClass = codeLanguage ? ` class="language-${escapeAttribute(codeLanguage)}"` : ''
        html.push(`<pre><code${languageClass}>${escapeHtml(codeFence.join('\n'))}</code></pre>`)
        codeFence = null
        codeLanguage = ''
      } else {
        codeFence = []
        codeLanguage = trimmed.slice(3).trim()
      }
      index += 1
      continue
    }

    if (codeFence) {
      codeFence.push(line)
      index += 1
      continue
    }

    if (!trimmed) {
      closeParagraph()
      closeList()
      index += 1
      continue
    }

    if (trimmed === '---' || trimmed === '***' || trimmed === '___') {
      closeParagraph()
      closeList()
      html.push('<hr>')
      index += 1
      continue
    }

    if (isMarkdownTableStart(lines, index)) {
      closeParagraph()
      closeList()
      const { html: tableHtml, nextIndex } = renderMarkdownTable(lines, index)
      html.push(tableHtml)
      index = nextIndex
      continue
    }

    if (isOutlineLine(trimmed)) {
      closeParagraph()
      closeList()
      const { html: outlineHtml, nextIndex, count } = parseOutlineItems(lines, index, countLeadingIndent(line))
      html.push(
        '<details class="ai-outline-block" open>'
          + `<summary class="ai-outline-summary">知识点大纲 · ${count} 项</summary>`
          + outlineHtml
          + '</details>',
      )
      index = nextIndex
      continue
    }

    const heading = trimmed.match(/^(#{1,4})\s+(.+)$/)
    if (heading) {
      closeParagraph()
      closeList()
      const level = heading[1].length + 1
      html.push(`<h${level}>${inlineMarkdown(heading[2])}</h${level}>`)
      index += 1
      continue
    }

    const unordered = trimmed.match(/^[-*]\s+(.+)$/)
    if (unordered) {
      closeParagraph()
      openList('ul')
      html.push(`<li>${inlineMarkdown(unordered[1])}</li>`)
      index += 1
      continue
    }

    const ordered = trimmed.match(/^\d+[.)]\s+(.+)$/)
    if (ordered) {
      closeParagraph()
      openList('ol')
      orderedItemIndex += 1
      const actionText = ordered[1].trim()
      html.push(
        `<li class="ai-action-item" role="button" tabindex="0" data-action="${escapeHtml(actionText)}">`
          + `<span class="ai-action-index">${orderedItemIndex}</span>`
          + `<span class="ai-action-text">${inlineMarkdown(actionText)}</span>`
          + '</li>',
      )
      index += 1
      continue
    }

    if (trimmed.startsWith('>')) {
      closeParagraph()
      closeList()
      html.push(`<blockquote>${inlineMarkdown(trimmed.replace(/^>\s?/, ''))}</blockquote>`)
      index += 1
      continue
    }

    paragraph.push(trimmed)
    index += 1
  }

  closeParagraph()
  closeList()
  if (codeFence) {
    const languageClass = codeLanguage ? ` class="language-${escapeAttribute(codeLanguage)}"` : ''
    html.push(`<pre><code${languageClass}>${escapeHtml(codeFence.join('\n'))}</code></pre>`)
  }

  return html.join('')
}

const CIRCLED_NUMBER_PATTERN = /^[①-⑳]/

function isOutlineLine(trimmed: string) {
  return CIRCLED_NUMBER_PATTERN.test(trimmed)
}

function countLeadingIndent(line: string) {
  const match = line.match(/^[ \t]*/)
  if (!match) return 0
  return match[0].replace(/\t/g, '  ').length
}

function stripOutlineMarker(trimmed: string) {
  return trimmed.replace(CIRCLED_NUMBER_PATTERN, '').replace(/^\s*[-*]\s+/, '').trim()
}

function parseOutlineItems(lines: string[], startIndex: number, baseIndent: number) {
  const items: string[] = []
  let index = startIndex
  let count = 0

  while (index < lines.length) {
    const line = lines[index]
    const trimmed = line.trim()
    if (!trimmed || countLeadingIndent(line) > baseIndent || !isOutlineLine(trimmed)) break

    const text = stripOutlineMarker(trimmed)
    count += 1
    index += 1

    const nestedItems: string[] = []
    while (index < lines.length) {
      const nestedLine = lines[index]
      const nestedTrimmed = nestedLine.trim()
      if (!nestedTrimmed || countLeadingIndent(nestedLine) <= baseIndent) break
      nestedItems.push(`<li>${inlineMarkdown(stripOutlineMarker(nestedTrimmed))}</li>`)
      index += 1
    }

    const nestedHtml = nestedItems.length
      ? `<ul class="ai-outline-sublist">${nestedItems.join('')}</ul>`
      : ''
    items.push(
      `<li class="ai-outline-item">`
        + `<span class="ai-outline-text">${inlineMarkdown(text)}</span>`
        + nestedHtml
        + '</li>',
    )
  }

  return {
    html: `<ol class="ai-outline-list">${items.join('')}</ol>`,
    nextIndex: index,
    count,
  }
}

function isMarkdownTableStart(lines: string[], index: number) {
  const header = lines[index]?.trim() || ''
  const separator = lines[index + 1]?.trim() || ''
  return isMarkdownTableRow(header) && isMarkdownTableSeparator(separator)
}

function isMarkdownTableRow(line: string) {
  return line.startsWith('|') && line.endsWith('|') && line.split('|').length >= 4
}

function isMarkdownTableSeparator(line: string) {
  if (!isMarkdownTableRow(line)) return false
  return parseMarkdownTableRow(line).every((cell) => /^:?-{3,}:?$/.test(cell.trim()))
}

function renderMarkdownTable(lines: string[], startIndex: number) {
  const headerCells = parseMarkdownTableRow(lines[startIndex])
  const alignments = parseMarkdownTableRow(lines[startIndex + 1]).map(tableAlignment)
  const bodyRows: string[][] = []
  let index = startIndex + 2

  while (index < lines.length && isMarkdownTableRow(lines[index].trim())) {
    bodyRows.push(parseMarkdownTableRow(lines[index]))
    index += 1
  }

  const header = headerCells
    .map((cell, cellIndex) => (
      `<th${tableAlignAttribute(alignments[cellIndex])}>${inlineMarkdown(cell)}</th>`
    ))
    .join('')
  const rows = bodyRows
    .map((row) => {
      const cells = headerCells.map((_, cellIndex) => {
        const cell = row[cellIndex] || ''
        return `<td${tableAlignAttribute(alignments[cellIndex])}>${inlineMarkdown(cell)}</td>`
      })
      return `<tr>${cells.join('')}</tr>`
    })
    .join('')

  return {
    html: `<div class="table-scroll"><table><thead><tr>${header}</tr></thead><tbody>${rows}</tbody></table></div>`,
    nextIndex: index,
  }
}

function parseMarkdownTableRow(line: string) {
  return line
    .trim()
    .replace(/^\|/, '')
    .replace(/\|$/, '')
    .split('|')
    .map((cell) => cell.trim())
}

function tableAlignment(cell: string) {
  const trimmed = cell.trim()
  if (trimmed.startsWith(':') && trimmed.endsWith(':')) return 'center'
  if (trimmed.endsWith(':')) return 'right'
  return 'left'
}

function tableAlignAttribute(alignment: string | undefined) {
  if (!alignment || alignment === 'left') return ''
  return ` style="text-align:${alignment}"`
}

function inlineMarkdown(text: string) {
  return text
    .split(/(`[^`]*`)/g)
    .map((part) => {
      if (part.startsWith('`') && part.endsWith('`')) {
        return `<code>${escapeHtml(part.slice(1, -1))}</code>`
      }
      return escapeHtml(part)
        .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
        .replace(/\[([^\]]+)\]\((https?:\/\/[^)\s]+)\)/g, '<a href="$2" target="_blank" rel="noreferrer">$1</a>')
    })
    .join('')
}

function escapeHtml(value: string) {
  return value
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')
}

function escapeAttribute(value: string) {
  return value.replace(/[^a-zA-Z0-9_-]/g, '')
}
