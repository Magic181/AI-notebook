<template>
  <div v-if="citations.length" class="mt-2 space-y-2">
    <p class="text-xs text-[var(--text-secondary)]">引用来源</p>
    <div
      v-for="(citation, index) in citations"
      :key="citationKey(citation, index)"
      class="rounded-lg border border-[var(--border)] bg-[var(--bg)] p-3 text-xs text-[var(--text-secondary)]"
    >
      <template v-if="isWebCitation(citation)">
        <div class="flex items-start justify-between gap-3">
          <a
            :href="citation.url"
            target="_blank"
            rel="noreferrer"
            class="min-w-0 flex-1 truncate font-medium text-[var(--primary)] hover:underline"
          >
            {{ citation.title }}
          </a>
          <span class="shrink-0 text-[var(--text-secondary)]">网页 #{{ citation.position }}</span>
        </div>
        <p class="mt-1 break-words text-[var(--text-secondary)]">{{ citation.url }}</p>
        <p class="mt-2 line-clamp-3 break-words">{{ citation.content }}</p>
      </template>

      <template v-else>
        <div class="flex items-start justify-between gap-3">
          <p class="min-w-0 flex-1 truncate font-medium text-[var(--text)]">
            {{ citation.document_name }}
          </p>
          <span class="shrink-0 rounded bg-[var(--bg-secondary)] px-2 py-0.5 text-[var(--text-secondary)]">
            {{ documentSourceLabel(citation.document_source_type) }} #{{ citation.position }}
          </span>
        </div>
        <p
          v-if="documentSourceDetail(citation)"
          class="mt-1 text-[var(--text-secondary)]"
        >
          {{ documentSourceDetail(citation) }}
        </p>
        <p class="mt-2 line-clamp-3 break-words">{{ citation.chunk_text }}</p>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Citation, DocumentCitation, WebCitation } from '@/api/chat'

defineProps<{
  citations: Citation[]
}>()

function isWebCitation(citation: Citation): citation is WebCitation {
  return citation.source_type === 'web'
}

function citationKey(citation: Citation, index: number) {
  if (isWebCitation(citation)) return `web-${citation.url}-${citation.position}-${index}`
  return `doc-${citation.document_id}-${citation.chunk_id}-${citation.position}-${index}`
}

function documentSourceLabel(sourceType?: string) {
  const labels: Record<string, string> = {
    paragraph: '正文',
    heading: '标题',
    page: '页面',
    table: '表格',
    code: '代码',
    image_ocr: '图片 OCR',
    image_caption: '图片描述',
    mixed: '混合',
    text: '文本',
  }
  return labels[sourceType || ''] || '文本'
}

function documentSourceDetail(citation: DocumentCitation) {
  const metadata = citation.metadata || {}
  const parts: string[] = []
  const page = numberValue(metadata.page)
  const headingLevel = numberValue(metadata.heading_level)
  const tableIndex = numberValue(metadata.table_index)
  const assetPosition = numberValue(metadata.asset_position)
  const language = stringValue(metadata.language)

  if (page) parts.push(`第 ${page} 页`)
  if (headingLevel) parts.push(`${headingLevel} 级标题`)
  if (tableIndex) parts.push(`表格 ${tableIndex}`)
  if (assetPosition !== null) parts.push(`图片 ${assetPosition + 1}`)
  if (language) parts.push(language)
  return parts.join(' · ')
}

function numberValue(value: unknown) {
  return typeof value === 'number' ? value : null
}

function stringValue(value: unknown) {
  return typeof value === 'string' && value.trim() ? value.trim() : ''
}
</script>
