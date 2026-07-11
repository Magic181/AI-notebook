<template>
  <div v-if="loading" class="py-10 text-center text-sm text-content-secondary">
    加载文档中...
  </div>

  <div v-else-if="documents.length === 0" class="py-6 text-center text-sm text-content-secondary">
    暂无文档，上传第一个文件开始构建知识库
  </div>

  <div v-else class="space-y-3">
    <div
      v-for="doc in documents"
      :key="doc.id"
      class="flex flex-col gap-3 rounded-card border border-line bg-surface-elevated p-4 shadow-card-default transition-shadow hover:shadow-card-hover sm:flex-row sm:items-center"
    >
      <div class="flex min-w-0 flex-1 items-start gap-3">
        <div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-gmd bg-primary-soft text-xs font-bold uppercase text-primary">
          {{ fileBadge(doc.file_type) }}
        </div>

        <div class="min-w-0 flex-1">
          <p class="break-words font-medium text-content">{{ doc.name }}</p>
          <p class="mt-1 text-xs text-content-secondary">
            {{ formatSize(doc.file_size) }}
          </p>
          <p v-if="doc.status === 'failed'" class="mt-1 break-words text-xs text-red-500">
            解析失败，可重新解析。
          </p>
        </div>
      </div>

      <div class="flex shrink-0 items-center justify-between gap-3 sm:justify-end">
        <span
          class="rounded-pill px-3 py-1 text-xs font-medium"
          :class="statusClass(doc.status)"
        >
          {{ statusLabel(doc.status) }}
        </span>

        <button
          :disabled="isReparseDisabled(doc)"
          class="kit-button kit-button-ghost kit-button-sm"
          @click="$emit('reparse', doc)"
        >
          {{ isReparsing(doc.id) ? '入队中...' : '重新解析' }}
        </button>

        <button
          class="kit-button kit-button-danger kit-button-sm"
          @click="$emit('delete', doc)"
        >
          删除
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Document, DocumentStatus } from '@/api/document'

const props = defineProps<{
  documents: Document[]
  loading?: boolean
  reparsingIds?: number[]
}>()

defineEmits<{
  delete: [document: Document]
  reparse: [document: Document]
}>()

function fileBadge(type: string) {
  const badges: Record<string, string> = {
    pdf: 'PDF',
    docx: 'DOC',
    md: 'MD',
    txt: 'TXT',
  }
  return badges[type] || 'FILE'
}

function formatSize(bytes: number) {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

function statusLabel(status: DocumentStatus) {
  const labels: Record<DocumentStatus, string> = {
    uploading: '上传中',
    parsing: '解析中',
    completed: '已完成',
    failed: '失败',
  }
  return labels[status]
}

function statusClass(status: DocumentStatus) {
  const classes: Record<DocumentStatus, string> = {
    uploading: 'bg-blue-500/10 text-blue-600',
    parsing: 'bg-amber-500/10 text-amber-600',
    completed: 'bg-green-500/10 text-green-600',
    failed: 'bg-red-500/10 text-red-500',
  }
  return classes[status]
}

function isActiveStatus(status: DocumentStatus) {
  return status === 'uploading' || status === 'parsing'
}

function isReparsing(documentId: number) {
  return Boolean(props.reparsingIds?.includes(documentId))
}

function isReparseDisabled(document: Document) {
  return isActiveStatus(document.status) || isReparsing(document.id)
}
</script>
