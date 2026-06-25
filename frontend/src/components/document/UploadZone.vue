<template>
  <div
    class="rounded-lg border-2 border-dashed border-[var(--border)] bg-[var(--bg-secondary)] p-6 text-center transition-colors"
    :class="[
      isDragging ? 'border-[var(--primary)] bg-[var(--primary)]/5' : '',
      uploading ? 'pointer-events-none opacity-70' : '',
    ]"
    @dragover.prevent="isDragging = true"
    @dragleave.prevent="isDragging = false"
    @drop.prevent="handleDrop"
  >
    <div class="mx-auto flex h-11 w-11 items-center justify-center rounded-lg border border-[var(--border)] bg-[var(--bg)]">
      <span class="h-5 w-5 rounded border-2 border-[var(--primary)] border-t-transparent" />
    </div>
    <p class="mt-3 font-medium text-[var(--text)]">拖拽文件到此处上传</p>
    <p class="mt-2 text-sm text-[var(--text-secondary)]">
      支持 TXT、MD、PDF、DOCX，单文件最大 20MB
    </p>
    <p v-if="isDragging" class="mt-2 text-xs font-medium text-[var(--primary)]">
      松开鼠标开始上传
    </p>
    <label class="mt-4 inline-block cursor-pointer">
      <input
        type="file"
        class="hidden"
        multiple
        accept=".txt,.md,.markdown,.pdf,.docx"
        :disabled="uploading"
        @change="handleFileSelect"
      />
      <span
        class="inline-flex rounded-lg bg-[var(--primary)] px-5 py-2.5 text-sm font-medium text-white hover:bg-[var(--primary-hover)]"
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
