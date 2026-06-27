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
        <div
          v-if="documentEvidenceBadges(citation).length"
          class="mt-2 flex flex-wrap gap-1.5"
        >
          <span
            v-for="badge in documentEvidenceBadges(citation)"
            :key="badge"
            class="rounded border border-[var(--border)] bg-[var(--bg-secondary)] px-1.5 py-0.5 text-[11px] text-[var(--text-secondary)]"
          >
            {{ badge }}
          </span>
        </div>
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
  const assetName = stringValue(metadata.asset_name)
  const visionProvider = stringValue(metadata.vision_provider)
  const visionModel = stringValue(metadata.vision_model)
  const source = stringValue(metadata.source)
  const target = stringValue(metadata.target)

  if (page !== null) parts.push(`第 ${page} 页`)
  if (headingLevel !== null) parts.push(`${headingLevel} 级标题`)
  if (tableIndex !== null) parts.push(`表格 ${displayIndex(tableIndex)}`)
  if (assetPosition !== null) parts.push(`图片 ${assetPosition + 1}`)
  if (language) parts.push(language)
  if (assetName) parts.push(assetName)
  if (visionProvider) parts.push(`视觉服务 ${visionProvider}`)
  if (visionModel) parts.push(`视觉 ${visionModel}`)
  if (source) parts.push(source)
  if (target) parts.push(target)
  return parts.join(' · ')
}

function documentEvidenceBadges(citation: DocumentCitation) {
  const metadata = citation.metadata || {}
  const badges: string[] = []
  const reason = stringValue(metadata.retrieval_reason)
  const score = numberValue(metadata.retrieval_score)

  if (reason) {
    badges.push(
      ...reason
        .split('+')
        .map((item) => retrievalReasonLabel(item))
        .filter(Boolean),
    )
  }
  if (score !== null) badges.push(`相关度 ${score}`)
  return [...new Set(badges)]
}

function retrievalReasonLabel(reason: string) {
  const labels: Record<string, string> = {
    keyword_match: '关键词命中',
    source_intent: '类型匹配',
    document_context: '文档上下文',
  }
  return labels[reason] || ''
}

function displayIndex(value: number) {
  return value <= 0 ? value + 1 : value
}

function numberValue(value: unknown) {
  return typeof value === 'number' ? value : null
}

function stringValue(value: unknown) {
  return typeof value === 'string' && value.trim() ? value.trim() : ''
}
</script>
