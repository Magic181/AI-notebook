<template>
  <div class="flex h-full flex-col">
    <header class="flex h-14 shrink-0 items-center justify-between border-b border-[var(--border)] px-6">
      <div>
        <h2 class="font-medium text-[var(--text)]">{{ notebook?.name || 'Notebook' }}</h2>
        <p v-if="notebook?.description" class="text-sm text-[var(--text-secondary)]">
          {{ notebook.description }}
        </p>
      </div>
      <router-link
        v-if="notebook"
        :to="`/chat/${notebook.id}`"
        class="rounded-xl bg-[var(--primary)] px-4 py-2 text-sm font-medium text-white hover:bg-[var(--primary-hover)]"
      >
        开始对话
      </router-link>
    </header>

    <div class="flex-1 overflow-y-auto p-6">
      <div class="rounded-2xl border border-dashed border-[var(--border)] py-16 text-center">
        <p class="text-4xl">📄</p>
        <p class="mt-4 text-[var(--text)]">文档管理</p>
        <p class="mt-2 text-sm text-[var(--text-secondary)]">
          上传文档后，AI 将自动阅读并建立知识索引
        </p>
        <p class="mt-4 text-xs text-[var(--text-secondary)]">（Batch 4 实现）</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useNotebookStore } from '@/stores/notebook'

const route = useRoute()
const notebookStore = useNotebookStore()

const notebook = computed(() => notebookStore.currentNotebook)

onMounted(() => {
  const id = Number(route.params.id)
  if (id) notebookStore.fetchNotebook(id).catch(() => {})
})
</script>
