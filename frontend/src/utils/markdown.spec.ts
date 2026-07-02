import { describe, expect, it } from 'vitest'
import { markdownToHtml } from './markdown'

describe('markdownToHtml', () => {
  it('renders paragraphs, headings, strong text, inline code and links', () => {
    const html = markdownToHtml('# Title\n\nHello **AI** `code` [link](https://example.com)')

    expect(html).toContain('<h2>Title</h2>')
    expect(html).toContain('<p>Hello <strong>AI</strong> <code>code</code> <a href="https://example.com" target="_blank" rel="noreferrer">link</a></p>')
  })

  it('escapes raw html while preserving inline markdown formatting', () => {
    const html = markdownToHtml('Hello <script>alert("x")</script> and **safe**')

    expect(html).toContain('&lt;script&gt;alert(&quot;x&quot;)&lt;/script&gt;')
    expect(html).toContain('<strong>safe</strong>')
    expect(html).not.toContain('<script>')
  })

  it('renders fenced code blocks with sanitized language classes', () => {
    const html = markdownToHtml('```ts<script>\nconst value = "<tag>"\n```')

    expect(html).toContain('<pre><code class="language-tsscript">')
    expect(html).toContain('const value = &quot;&lt;tag&gt;&quot;')
  })

  it('renders markdown tables with alignment', () => {
    const html = markdownToHtml('| Name | Score |\n| --- | ---: |\n| Ada | 99 |')

    expect(html).toContain('<div class="table-scroll"><table>')
    expect(html).toContain('<th>Name</th>')
    expect(html).toContain('<th style="text-align:right">Score</th>')
    expect(html).toContain('<td style="text-align:right">99</td>')
  })

  it('renders ordered items as clickable action items', () => {
    const html = markdownToHtml('1. Summarize document\n2. Find risks')

    expect(html).toContain('<ol class="ai-action-list">')
    expect(html).toContain('data-action="Summarize document"')
    expect(html).toContain('<span class="ai-action-index">2</span>')
  })

  it('renders circled-number outlines as collapsible outline blocks', () => {
    const html = markdownToHtml('① 第一章\n  - 重点 A\n② 第二章')

    expect(html).toContain('<details class="ai-outline-block" open>')
    expect(html).toContain('知识点大纲 · 2 项')
    expect(html).toContain('<span class="ai-outline-text">第一章</span>')
    expect(html).toContain('<ul class="ai-outline-sublist"><li>重点 A</li></ul>')
  })
})
