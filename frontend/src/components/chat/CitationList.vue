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
        <p class="mt-2 line-clamp-3 break-words">{{ citation.chunk_text }}</p>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Citation, WebCitation } from '@/api/chat'

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
    page: '页面',
    table: '表格',
    mixed: '混合',
    text: '文本',
  }
  return labels[sourceType || ''] || '文本'
}
</script>
