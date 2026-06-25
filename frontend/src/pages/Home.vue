<template>
  <div class="flex h-full flex-col">
    <header class="flex h-14 shrink-0 items-center justify-between border-b border-[var(--border)] px-6">
      <div>
        <h1 class="text-lg font-semibold text-[var(--text)]">我的笔记本</h1>
        <p class="text-sm text-[var(--text-secondary)]">管理你的 AI 知识库</p>
      </div>
      <button
        class="rounded-lg bg-[var(--primary)] px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-[var(--primary-hover)]"
        @click="showCreate = true"
      >
        新建笔记本
      </button>
    </header>

    <div class="flex flex-col gap-3 border-b border-[var(--border)] px-6 py-3 sm:flex-row sm:items-center">
      <input
        v-model="search"
        type="text"
        placeholder="搜索笔记本..."
        class="min-w-0 flex-1 rounded-lg border border-[var(--border)] bg-[var(--bg)] px-4 py-2 text-sm text-[var(--text)] outline-none focus:border-[var(--primary)]"
      />
      <button
        class="rounded-lg px-4 py-2 text-sm transition-colors sm:shrink-0"
        :class="
          favoriteOnly
            ? 'bg-[var(--primary)]/10 text-[var(--primary)]'
            : 'text-[var(--text-secondary)] hover:bg-[var(--bg-secondary)]'
        "
        @click="toggleFavoriteFilter"
      >
        {{ favoriteOnly ? '仅看收藏' : '收藏筛选' }}
      </button>
    </div>

    <div class="flex-1 overflow-y-auto p-6">
      <div v-if="notebookStore.loading" class="flex items-center justify-center py-20">
        <p class="text-[var(--text-secondary)]">加载中...</p>
      </div>

      <div
        v-else-if="notebookStore.notebooks.length === 0"
        class="flex flex-col items-center justify-center rounded-lg border border-dashed border-[var(--border)] py-20 text-center"
      >
        <div class="mb-4 h-10 w-10 rounded-lg border border-[var(--border)] bg-[var(--bg-secondary)]" />
        <p class="text-lg font-medium text-[var(--text)]">
          {{ emptyTitle }}
        </p>
        <p class="mt-2 text-sm text-[var(--text-secondary)]">{{ emptyHint }}</p>
        <button
          v-if="!favoriteOnly && !search"
          class="mt-6 rounded-lg bg-[var(--primary)] px-5 py-2.5 text-sm font-medium text-white hover:bg-[var(--primary-hover)]"
          @click="showCreate = true"
        >
          创建笔记本
        </button>
      </div>

      <div v-else class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        <div
          v-for="nb in notebookStore.notebooks"
          :key="nb.id"
          class="group relative rounded-lg border border-[var(--border)] bg-[var(--bg)] p-5 transition-all hover:border-[var(--primary)]/40 hover:shadow-md"
        >
          <button
            class="absolute right-4 top-4 rounded-full px-2 py-1 text-xs transition-colors"
            :class="
              nb.is_favorite
                ? 'bg-yellow-500/10 text-yellow-600'
                : 'text-[var(--text-secondary)] hover:bg-[var(--bg-secondary)]'
            "
            @click="handleToggleFavorite(nb.id)"
          >
            {{ nb.is_favorite ? '已收藏' : '收藏' }}
          </button>

          <router-link :to="`/notebook/${nb.id}`" class="block pr-20">
            <h3 class="font-medium text-[var(--text)] group-hover:text-[var(--primary)]">
              {{ nb.name }}
            </h3>
            <p class="mt-2 line-clamp-2 text-sm text-[var(--text-secondary)]">
              {{ nb.description || '暂无描述' }}
            </p>
            <p class="mt-4 text-xs text-[var(--text-secondary)]">
              更新于 {{ formatDate(nb.updated_at) }}
            </p>
            <p class="mt-2 text-xs text-[var(--text-secondary)]">
              {{ nb.document_count || 0 }} 个文档
            </p>
          </router-link>
        </div>
      </div>
    </div>
  </div>

  <div
    v-if="showCreate"
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/40"
    @click.self="showCreate = false"
  >
    <div class="w-full max-w-md rounded-lg bg-[var(--bg)] p-6 shadow-xl">
      <h2 class="text-lg font-semibold text-[var(--text)]">新建笔记本</h2>
      <form class="mt-4 space-y-4" @submit.prevent="handleCreate">
        <input
          v-model="form.name"
          type="text"
          placeholder="笔记本名称"
          required
          class="w-full rounded-lg border border-[var(--border)] bg-[var(--bg)] px-4 py-3 text-[var(--text)] outline-none focus:border-[var(--primary)]"
        />
        <textarea
          v-model="form.description"
          placeholder="描述（可选）"
          rows="3"
          class="w-full resize-none rounded-lg border border-[var(--border)] bg-[var(--bg)] px-4 py-3 text-[var(--text)] outline-none focus:border-[var(--primary)]"
        />
        <div class="flex justify-end gap-3">
          <button
            type="button"
            class="rounded-lg px-4 py-2 text-sm text-[var(--text-secondary)] hover:bg-[var(--bg-secondary)]"
            @click="showCreate = false"
          >
            取消
          </button>
          <button
            type="submit"
            :disabled="creating"
            class="rounded-lg bg-[var(--primary)] px-4 py-2 text-sm font-medium text-white hover:bg-[var(--primary-hover)] disabled:opacity-50"
          >
            {{ creating ? '创建中...' : '创建' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useNotebookStore } from '@/stores/notebook'

const router = useRouter()
const notebookStore = useNotebookStore()

const showCreate = ref(false)
const creating = ref(false)
const search = ref('')
const favoriteOnly = ref(false)
const form = ref({ name: '', description: '' })

const emptyTitle = computed(() => {
  if (favoriteOnly.value) return '暂无收藏的笔记本'
  if (search.value.trim()) return '未找到匹配的笔记本'
  return '还没有笔记本'
})

const emptyHint = computed(() => {
  if (favoriteOnly.value || search.value.trim()) return '试试调整筛选条件'
  return '创建第一个笔记本，开始整理你的知识'
})

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

function loadNotebooks() {
  notebookStore.fetchNotebooks({
    search: search.value.trim() || undefined,
    is_favorite: favoriteOnly.value || undefined,
  }).catch(() => {})
}

function toggleFavoriteFilter() {
  favoriteOnly.value = !favoriteOnly.value
  loadNotebooks()
}

async function handleToggleFavorite(id: number) {
  try {
    await notebookStore.toggleFavorite(id)
  } catch {
    // error shown by axios interceptor
  }
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

let searchTimer: ReturnType<typeof setTimeout> | null = null
watch(search, () => {
  if (searchTimer) clearTimeout(searchTimer)
  searchTimer = setTimeout(loadNotebooks, 300)
})

onMounted(loadNotebooks)
onUnmounted(() => {
  if (searchTimer) clearTimeout(searchTimer)
})
</script>
