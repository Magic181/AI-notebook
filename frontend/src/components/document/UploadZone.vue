<template>
  <div
    class="rounded-glg border-2 border-dashed border-line bg-surface-secondary p-8 text-center transition-all"
    :class="[
      isDragging ? 'border-primary bg-primary-soft' : 'hover:border-primary/40',
      uploading ? 'pointer-events-none opacity-70' : '',
    ]"
    @dragover.prevent="isDragging = true"
    @dragleave.prevent="isDragging = false"
    @drop.prevent="handleDrop"
  >
    <div class="mx-auto flex h-14 w-14 items-center justify-center rounded-control bg-primary text-ink shadow-gmd">
      <svg viewBox="0 0 24 24" class="h-6 w-6" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
        <polyline points="17 8 12 3 7 8" />
        <line x1="12" y1="3" x2="12" y2="15" />
      </svg>
    </div>
    <p class="mt-4 font-medium text-content">拖拽文件到此处上传</p>
    <p class="mt-2 text-sm text-content-secondary">
      支持 TXT、MD、PDF、DOCX，单文件最大 20MB
    </p>
    <p v-if="isDragging" class="mt-2 text-xs font-medium text-primary">
      松开鼠标开始上传
    </p>
    <label class="mt-5 inline-block cursor-pointer">
      <input
        type="file"
        class="hidden"
        multiple
        accept=".txt,.md,.markdown,.pdf,.docx"
        :disabled="uploading"
        @change="handleFileSelect"
      />
      <span
        class="kit-button kit-button-primary"
        :class="uploading ? 'pointer-events-none opacity-50' : ''"
      >
        {{ uploading ? '上传中...' : '选择文件' }}
      </span>
    </label>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

defineProps<{
  uploading?: boolean
}>()

const emit = defineEmits<{
  upload: [files: File[]]
}>()

const isDragging = ref(false)

function emitFiles(fileList: FileList | null) {
  if (!fileList?.length) return
  emit('upload', Array.from(fileList))
}

function handleDrop(event: DragEvent) {
  isDragging.value = false
  emitFiles(event.dataTransfer?.files ?? null)
}

function handleFileSelect(event: Event) {
  const input = event.target as HTMLInputElement
  emitFiles(input.files)
  input.value = ''
}
</script>
