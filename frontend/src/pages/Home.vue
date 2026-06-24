<template>
  <div class="flex h-full flex-col">
    <header class="flex h-14 shrink-0 items-center justify-between border-b border-[var(--border)] px-6">
      <div>
        <h1 class="text-lg font-semibold text-[var(--text)]">我的笔记本</h1>
        <p class="text-sm text-[var(--text-secondary)]">管理你的 AI 知识库</p>
      </div>
      <button
        class="rounded-xl bg-[var(--primary)] px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-[var(--primary-hover)]"
        @click="showCreate = true"
      >
        + 新建笔记本
      </button>
    </header>

    <div class="flex-1 overflow-y-auto p-6">
      <div v-if="notebookStore.loading" class="flex items-center justify-center py-20">
        <p class="text-[var(--text-secondary)]">加载中...</p>
      </div>

      <div
        v-else-if="notebookStore.notebooks.length === 0"
        class="flex flex-col items-center justify-center rounded-2xl border border-dashed border-[var(--border)] py-20"
      >
        <p class="text-4xl">📓</p>
        <p class="mt-4 text-lg font-medium text-[var(--text)]">还没有笔记本</p>
        <p class="mt-2 text-sm text-[var(--text-secondary)]">创建第一个笔记本，开始整理你的知识</p>
        <button
          class="mt-6 rounded-xl bg-[var(--primary)] px-5 py-2.5 text-sm font-medium text-white hover:bg-[var(--primary-hover)]"
          @click="showCreate = true"
        >
          创建笔记本
        </button>
      </div>

      <div v-else class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        <router-link
          v-for="nb in notebookStore.notebooks"
          :key="nb.id"
          :to="`/notebook/${nb.id}`"
          class="group rounded-2xl border border-[var(--border)] bg-[var(--bg)] p-5 transition-all hover:border-[var(--primary)]/40 hover:shadow-md"
        >
          <div class="flex items-start justify-between">
            <h3 class="font-medium text-[var(--text)] group-hover:text-[var(--primary)]">
              {{ nb.name }}
            </h3>
            <span v-if="nb.is_favorite" class="text-sm">⭐</span>
          </div>
          <p class="mt-2 line-clamp-2 text-sm text-[var(--text-secondary)]">
            {{ nb.description || '暂无描述' }}
          </p>
          <p class="mt-4 text-xs text-[var(--text-secondary)]">
            更新于 {{ formatDate(nb.updated_at) }}
          </p>
        </router-link>
      </div>
    </div>

  </div>

  <div
    v-if="showCreate"
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/40"
    @click.self="showCreate = false"
  >
    <div class="w-full max-w-md rounded-2xl bg-[var(--bg)] p-6 shadow-xl">
      <h2 class="text-lg font-semibold text-[var(--text)]">新建笔记本</h2>
      <form class="mt-4 space-y-4" @submit.prevent="handleCreate">
        <input
          v-model="form.name"
          type="text"
          placeholder="笔记本名称"
          required
          class="w-full rounded-xl border border-[var(--border)] bg-[var(--bg)] px-4 py-3 text-[var(--text)] outline-none focus:border-[var(--primary)]"
        />
        <textarea
          v-model="form.description"
          placeholder="描述（可选）"
          rows="3"
          class="w-full resize-none rounded-xl border border-[var(--border)] bg-[var(--bg)] px-4 py-3 text-[var(--text)] outline-none focus:border-[var(--primary)]"
        />
        <div class="flex justify-end gap-3">
          <button
            type="button"
            class="rounded-xl px-4 py-2 text-sm text-[var(--text-secondary)] hover:bg-[var(--bg-secondary)]"
            @click="showCreate = false"
          >
            取消
          </button>
          <button
            type="submit"
            :disabled="creating"
            class="rounded-xl bg-[var(--primary)] px-4 py-2 text-sm font-medium text-white hover:bg-[var(--primary-hover)] disabled:opacity-50"
          >
            {{ creating ? '创建中...' : '创建' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useNotebookStore } from '@/stores/notebook'

const router = useRouter()
const notebookStore = useNotebookStore()

const showCreate = ref(false)
const creating = ref(false)
const form = ref({ name: '', description: '' })

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

async function handleCreate() {
  if (!form.value.name.trim()) return
  creating.value = true
  try {
    const notebook = await notebookStore.createNotebook({
      name: form.value.name.trim(),
      description: form.value.description.trim(),
    })
    showCreate.value = false
    form.value = { name: '', description: '' }
    ElMessage.success('创建成功')
    router.push(`/notebook/${notebook.id}`)
  } catch {
    // error shown by axios interceptor
  } finally {
    creating.value = false
  }
}

onMounted(() => {
  notebookStore.fetchNotebooks().catch(() => {})
})
</script>
