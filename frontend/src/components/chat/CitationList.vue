<template>
  <div v-if="citations.length" class="citation-section">
    <div class="citation-section-header">
      <div class="flex items-center gap-2">
        <span class="citation-section-mark" />
        <p class="text-xs font-semibold text-content-secondary">引用来源</p>
      </div>
      <div class="flex items-center gap-2">
        <span class="text-[11px] text-content-secondary">
          {{ citationCountLabel }}
        </span>
        <button
          v-if="canToggle"
          type="button"
          class="citation-toggle"
          :aria-expanded="isExpanded"
          @click="isExpanded = !isExpanded"
        >
          <svg
            viewBox="0 0 24 24"
            class="h-3.5 w-3.5 transition-transform duration-200"
            :class="isExpanded ? 'rotate-180' : ''"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <path d="m6 9 6 6 6-6" />
          </svg>
          <span>{{ isExpanded ? '收起' : `展开 ${hiddenCitationCount} 条` }}</span>
        </button>
      </div>
    </div>
    <div
      v-for="(citation, index) in visibleCitations"
      :key="citationKey(citation, index)"
      class="citation-card group p-4 text-sm transition-all duration-300"
    >
      <template v-if="isWebCitation(citation)">
        <div class="flex items-start justify-between gap-3">
          <div class="flex min-w-0 items-center gap-3">
            <span class="citation-icon">
              <svg viewBox="0 0 24 24" class="h-4 w-4" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10" />
                <path d="M2 12h20" />
                <path d="M12 2a15.3 15.3 0 0 1 0 20" />
                <path d="M12 2a15.3 15.3 0 0 0 0 20" />
              </svg>
            </span>
            <a
              :href="citation.url"
              target="_blank"
              rel="noreferrer"
              class="min-w-0 truncate text-[15px] font-semibold text-content transition-colors group-hover:text-primary"
            >
              {{ citation.title }}
            </a>
          </div>
          <span class="citation-meta">网页 #{{ citation.position }}</span>
        </div>
        <div class="mt-3 flex flex-wrap gap-1.5">
          <span class="citation-tag">联网来源</span>
        </div>
        <p class="mt-2 break-words text-xs text-content-secondary">{{ citation.url }}</p>
        <p
          class="mt-2 break-words text-sm leading-6 text-content-secondary"
          :class="isExpanded ? 'line-clamp-4' : 'line-clamp-2'"
        >
          {{ citation.content }}
        </p>
      </template>

      <template v-else>
        <div class="flex items-start justify-between gap-3">
          <div class="flex min-w-0 items-center gap-3">
            <span class="citation-icon">
              <svg viewBox="0 0 24 24" class="h-4 w-4" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                <path d="M14 2v6h6" />
                <path d="M8 13h8" />
                <path d="M8 17h5" />
              </svg>
            </span>
            <p class="min-w-0 truncate text-[15px] font-semibold text-content">
              {{ citation.document_name }}
            </p>
          </div>
          <span class="citation-meta">
            {{ documentMetaLabel(citation) }}
          </span>
        </div>
        <p
          v-if="documentSourceDetail(citation)"
          class="mt-2 text-xs leading-5 text-content-secondary"
        >
          {{ documentSourceDetail(citation) }}
        </p>
        <div
          v-if="documentEvidenceBadges(citation).length || relevanceTier(citation)"
          class="mt-2 flex flex-wrap gap-1.5"
        >
          <span
            v-if="relevanceTier(citation)"
            class="citation-tag"
            :class="`citation-tag-relevance-${relevanceTier(citation)!.tone}`"
          >
            {{ relevanceTier(citation)!.label }}
          </span>
          <span
            v-for="badge in documentEvidenceBadges(citation)"
            :key="badge.label"
            class="citation-tag"
            :class="badge.tone === 'neutral' ? 'citation-tag-neutral' : ''"
          >
            {{ badge.label }}
          </span>
        </div>
        <p
          class="mt-3 break-words text-sm leading-6 text-content-secondary"
          :class="isExpanded ? 'line-clamp-4' : 'line-clamp-2'"
        >
          {{ citationPreview(citation) }}
        </p>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import type { Citation, DocumentCitation, WebCitation } from '@/api/chat'

const props = defineProps<{
  citations: Citation[]
}>()

const collapsedLimit = 3
const isExpanded = ref(false)

const canToggle = computed(() => props.citations.length > collapsedLimit)
const visibleCitations = computed(() =>
  isExpanded.value ? props.citations : props.citations.slice(0, collapsedLimit),
)
const hiddenCitationCount = computed(() =>
  Math.max(0, props.citations.length - visibleCitations.value.length),
)
const citationCountLabel = computed(() =>
  canToggle.value && !isExpanded.value
    ? `显示 ${visibleCitations.value.length} / ${props.citations.length}`
    : `${props.citations.length} 条证据`,
)

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

function documentMetaLabel(citation: DocumentCitation) {
  const metadata = citation.metadata || {}
  const page = numberValue(metadata.page)
  const tableIndex = numberValue(metadata.table_index)
  const assetPosition = numberValue(metadata.asset_position)

  if (assetPosition !== null) return `图 #${displayOrdinal(assetPosition)}`
  if (tableIndex !== null) return `表 #${displayOrdinal(tableIndex)}`
  if (page !== null) return `第 ${page} 页`
  return `${documentSourceLabel(citation.document_source_type)} #${citation.position}`
}

function documentSourceDetail(citation: DocumentCitation) {
  const metadata = citation.metadata || {}
  const parts: string[] = []
  const headingLevel = numberValue(metadata.heading_level)
  const language = stringValue(metadata.language)
  const assetName = stringValue(metadata.asset_name)
  const visionProvider = stringValue(metadata.vision_provider)
  const visionModel = stringValue(metadata.vision_model)
  const source = stringValue(metadata.source)
  const target = stringValue(metadata.target)

  parts.push(documentSourceLabel(citation.document_source_type))
  if (headingLevel !== null) parts.push(`${headingLevel} 级标题`)
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
  const badges: Array<{ label: string; tone?: 'green' | 'neutral' }> = []
  const reason = stringValue(metadata.retrieval_reason)

  if (reason) {
    badges.push(
      ...reason
        .split('+')
        .map((item) => retrievalReasonLabel(item))
        .filter(Boolean)
        .map((label) => ({ label })),
    )
  }

  const uniqueLabels = new Set<string>()
  return badges.filter((badge) => {
    if (uniqueLabels.has(badge.label)) return false
    uniqueLabels.add(badge.label)
    return true
  })
}

const maxRetrievalScore = computed(() => {
  let max = 0
  for (const citation of props.citations) {
    if (isWebCitation(citation)) continue
    const score = numberValue((citation.metadata || {}).retrieval_score)
    if (score !== null && score > max) max = score
  }
  return max
})

function relevanceTier(citation: DocumentCitation): { label: string; tone: 'high' | 'medium' | 'low' } | null {
  const score = numberValue((citation.metadata || {}).retrieval_score)
  if (score === null || maxRetrievalScore.value <= 0) return null
  const ratio = score / maxRetrievalScore.value
  if (ratio >= 0.66) return { label: '相关度: 高', tone: 'high' }
  if (ratio >= 0.33) return { label: '相关度: 中', tone: 'medium' }
  return { label: '相关度: 低', tone: 'low' }
}

function retrievalReasonLabel(reason: string) {
  const labels: Record<string, string> = {
    keyword_match: '关键词命中',
    source_intent: '类型匹配',
    document_context: '文档上下文',
  }
  return labels[reason] || ''
}

function citationPreview(citation: DocumentCitation) {
  return citation.chunk_text
    .replace(/^\[(图片\s*OCR|图片视觉描述|图片描述|表格|代码|正文|标题)\s*#?\d*\]\s*/i, '')
    .replace(/^OCR 文本：\s*/, '')
    .replace(/^视觉描述：\s*/, '')
    .trim()
}

function displayOrdinal(value: number) {
  return value + 1
}

function numberValue(value: unknown) {
  return typeof value === 'number' ? value : null
}

function stringValue(value: unknown) {
  return typeof value === 'string' && value.trim() ? value.trim() : ''
}
</script>

<style scoped>
.citation-section {
  margin-top: 1.75rem;
  padding-top: 1rem;
  border-top: 1px solid var(--border);
}

.citation-section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
  padding: 0 0.25rem;
}

.citation-section-mark {
  height: 0.375rem;
  width: 0.375rem;
  border-radius: 9999px;
  background: var(--primary);
}

.citation-card {
  margin-top: 0.75rem;
  border-radius: var(--radius-card);
  background: var(--bg-elevated);
  box-shadow: var(--shadow-default);
}

.citation-card:hover {
  background: var(--surface-hover);
  box-shadow: var(--shadow-hover);
}

.citation-toggle {
  display: inline-flex;
  min-height: 1.75rem;
  align-items: center;
  gap: 0.25rem;
  border-radius: var(--radius-control);
  border: 1px solid var(--border);
  background: var(--bg-elevated);
  padding: 0.25rem 0.55rem;
  color: var(--text-secondary);
  font-size: 0.72rem;
  font-weight: 600;
  line-height: 1;
  transition:
    background-color 160ms ease,
    border-color 160ms ease,
    color 160ms ease,
    transform 160ms ease;
}

.citation-toggle:hover {
  border-color: var(--primary);
  background: var(--primary-soft);
  color: var(--text);
}

.citation-toggle:active {
  transform: translateY(1px);
}

.citation-toggle:focus-visible {
  outline: 2px solid var(--primary);
  outline-offset: 2px;
}

.citation-icon {
  display: inline-flex;
  height: 2rem;
  width: 2rem;
  flex-shrink: 0;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-control);
  color: var(--primary-contrast);
  background: var(--primary);
}

.citation-meta {
  flex-shrink: 0;
  border-radius: var(--radius-control);
  border: 1px solid var(--border);
  background: var(--bg-elevated);
  padding: 0.125rem 0.55rem;
  color: var(--text-secondary);
  font-size: 0.75rem;
  line-height: 1.35;
}

.citation-tag {
  display: inline-flex;
  align-items: center;
  border-radius: var(--radius-control);
  background: var(--primary-soft);
  padding: 0.25rem 0.625rem;
  color: var(--primary-hover);
  font-size: 0.72rem;
  font-weight: 600;
  line-height: 1.2;
}

.citation-tag-neutral {
  background: var(--bg-elevated);
  color: var(--text-secondary);
}

.citation-tag-relevance-high {
  background: var(--primary-soft);
  color: var(--status-high);
}

.citation-tag-relevance-medium {
  background: var(--status-medium-soft);
  color: var(--status-medium);
}

.citation-tag-relevance-low {
  background: var(--bg-secondary);
  color: var(--status-low);
}

</style>
