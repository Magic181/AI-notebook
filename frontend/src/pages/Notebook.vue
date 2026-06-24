<template>
  <div class="flex h-full flex-col">
    <header class="flex h-14 shrink-0 items-center justify-between border-b border-[var(--border)] px-6">
      <div class="min-w-0 flex-1">
        <h2 class="truncate font-medium text-[var(--text)]">
          {{ notebook?.name || 'Notebook' }}
        </h2>
        <p v-if="notebook?.description" class="truncate text-sm text-[var(--text-secondary)]">
          {{ notebook.description }}
        </p>
      </div>
      <div v-if="notebook" class="ml-4 flex shrink-0 items-center gap-2">
        <button
          class="rounded-xl px-3 py-2 text-sm transition-colors"
          :class="
            notebook.is_favorite
              ? 'bg-yellow-500/10 text-yellow-600'
              : 'text-[var(--text-secondary)] hover:bg-[var(--bg-secondary)]'
          "
          @click="handleToggleFavorite"
        >
          {{ notebook.is_favorite ? '★ 已收藏' : '☆ 收藏' }}
        </button>
        <button
          class="rounded-xl px-3 py-2 text-sm text-[var(--text-secondary)] hover:bg-[var(--bg-secondary)]"
          @click="showEdit = true"
        >
          编辑
        </button>
        <button
          class="rounded-xl px-3 py-2 text-sm text-red-500 hover:bg-red-50 dark:hover:bg-red-950/30"
          @click="showDelete = true"
        >
          删除
        </button>
        <router-link
          :to="`/chat/${notebook.id}`"
          class="rounded-xl bg-[var(--primary)] px-4 py-2 text-sm font-medium text-white hover:bg-[var(--primary-hover)]"
        >
          开始对话
        </router-link>
      </div>
    </header>

    <div class="flex-1 overflow-y-auto p-6">
      <div v-if="loading" class="flex items-center justify-center py-20">
        <p class="text-[var(--text-secondary)]">加载中...</p>
      </div>
      <div
        v-else-if="!notebook"
        class="flex flex-col items-center justify-center py-20 text-[var(--text-secondary)]"
      >
        <p>笔记本不存在或无权访问</p>
        <router-link to="/" class="mt-4 text-[var(--primary)] hover:underline">
          返回首页
        </router-link>
      </div>
      <div
        v-else
        class="rounded-2xl border border-dashed border-[var(--border)] py-16 text-center"
      >
        <p class="text-4xl">📄</p>
        <p class="mt-4 text-[var(--text)]">文档管理</p>
        <p class="mt-2 text-sm text-[var(--text-secondary)]">
          上传文档后，AI 将自动阅读并建立知识索引
        </p>
        <p class="mt-4 text-xs text-[var(--text-secondary)]">（Batch 4 实现）</p>
      </div>
    </div>
  </div>

  <div
    v-if="showEdit && notebook"
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/40"
    @click.self="showEdit = false"
  >
    <div class="w-full max-w-md rounded-2xl bg-[var(--bg)] p-6 shadow-xl">
      <h2 class="text-lg font-semibold text-[var(--text)]">编辑笔记本</h2>
      <form class="mt-4 space-y-4" @submit.prevent="handleUpdate">
        <input
          v-model="editForm.name"
          type="text"
          placeholder="笔记本名称"
          required
          class="w-full rounded-xl border border-[var(--border)] bg-[var(--bg)] px-4 py-3 text-[var(--text)] outline-none focus:border-[var(--primary)]"
        />
        <textarea
          v-model="editForm.description"
          placeholder="描述（可选）"
          rows="3"
          class="w-full resize-none rounded-xl border border-[var(--border)] bg-[var(--bg)] px-4 py-3 text-[var(--text)] outline-none focus:border-[var(--primary)]"
        />
        <div class="flex justify-end gap-3">
          <button
            type="button"
            class="rounded-xl px-4 py-2 text-sm text-[var(--text-secondary)] hover:bg-[var(--bg-secondary)]"
            @click="showEdit = false"
          >
            取消
          </button>
          <button
            type="submit"
            :disabled="saving"
            class="rounded-xl bg-[var(--primary)] px-4 py-2 text-sm font-medium text-white hover:bg-[var(--primary-hover)] disabled:opacity-50"
          >
            {{ saving ? '保存中...' : '保存' }}
          </button>
        </div>
      </form>
    </div>
  </div>

  <div
    v-if="showDelete && notebook"
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/40"
    @click.self="showDelete = false"
  >
    <div class="w-full max-w-sm rounded-2xl bg-[var(--bg)] p-6 shadow-xl">
      <h2 class="text-lg font-semibold text-[var(--text)]">确认删除</h2>
      <p class="mt-2 text-sm text-[var(--text-secondary)]">
        确定要删除「{{ notebook.name }}」吗？此操作不可恢复。
      </p>
      <div class="mt-6 flex justify-end gap-3">
        <button
          class="rounded-xl px-4 py-2 text-sm text-[var(--text-secondary)] hover:bg-[var(--bg-secondary)]"
          @click="showDelete = false"
        >
          取消
        </button>
        <button
          :disabled="deleting"
          class="rounded-xl bg-red-500 px-4 py-2 text-sm font-medium text-white hover:bg-red-600 disabled:opacity-50"
          @click="handleDelete"
        >
          {{ deleting ? '删除中...' : '删除' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useNotebookStore } from '@/stores/notebook'

const route = useRoute()
const router = useRouter()
const notebookStore = useNotebookStore()

const loading = ref(false)
const showEdit = ref(false)
const showDelete = ref(false)
const saving = ref(false)
const deleting = ref(false)
const editForm = ref({ name: '', description: '' })

const notebook = computed(() => notebookStore.currentNotebook)

watch(notebook, (value) => {
  if (value) {
    editForm.value = {
      name: value.name,
      description: value.description || '',
    }
  }
})

async function loadNotebook() {
  const id = Number(route.params.id)
  if (!id) return
  loading.value = true
  try {
    await notebookStore.fetchNotebook(id)
  } catch {
    notebookStore.currentNotebook = null
  } finally {
    loading.value = false
  }
}

async function handleToggleFavorite() {
  if (!notebook.value) return
  try {
    const updated = await notebookStore.toggleFavorite(notebook.value.id)
    ElMessage.success(updated.is_favorite ? '已收藏' : '已取消收藏')
  } catch {
    // error shown by axios interceptor
  }
}

async function handleUpdate() {
  if (!notebook.value || !editForm.value.name.trim()) return
  saving.value = true
  try {
    await notebookStore.updateNotebook(notebook.value.id, {
      name: editForm.value.name.trim(),
      description: editForm.value.description.trim(),
    })
    showEdit.value = false
    ElMessage.success('保存成功')
  } catch {
    // error shown by axios interceptor
  } finally {
    saving.value = false
  }
}

async function handleDelete() {
  if (!notebook.value) return
  deleting.value = true
  try {
    await notebookStore.deleteNotebook(notebook.value.id)
    ElMessage.success('已删除')
    router.push('/')
  } catch {
    // error shown by axios interceptor
  } finally {
    deleting.value = false
  }
}

onMounted(loadNotebook)
</script>
