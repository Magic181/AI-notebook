<template>
  <div class="flex h-full flex-col">
    <header class="flex h-16 shrink-0 items-center justify-between px-6">
      <div>
        <h1 class="text-xl font-semibold tracking-tight text-content">我的笔记本</h1>
        <p class="text-sm text-content-secondary">管理你的 AI 知识库</p>
      </div>
      <button
        class="gemini-btn gemini-btn-primary"
        @click="showCreate = true"
      >
        <span class="text-base leading-none">+</span>
        新建笔记本
      </button>
    </header>

    <div class="flex flex-col gap-3 px-6 pb-3 sm:flex-row sm:items-center">
      <input
        v-model="search"
        type="text"
        placeholder="搜索笔记本..."
        class="min-w-0 flex-1 rounded-pill border border-line bg-surface-secondary px-5 py-2.5 text-sm text-content outline-none transition-all placeholder:text-content-secondary focus:border-primary focus:bg-surface focus:ring-4 focus:ring-primary-soft"
      />
      <button
        class="gemini-btn sm:shrink-0"
        :class="
          favoriteOnly
            ? 'gemini-btn-tonal'
            : 'gemini-btn-ghost'
        "
        @click="toggleFavoriteFilter"
      >
        {{ favoriteOnly ? '仅看收藏' : '收藏筛选' }}
      </button>
    </div>

    <div class="flex-1 overflow-y-auto p-6">
      <div v-if="notebookStore.loading" class="flex items-center justify-center py-20">
        <p class="text-content-secondary">加载中...</p>
      </div>

      <div
        v-else-if="loadError"
        class="flex flex-col items-center justify-center rounded-glg border border-dashed border-line bg-surface-secondary py-20 text-center"
      >
        <p class="text-lg font-medium text-content">加载笔记本失败</p>
        <p class="mt-2 text-sm text-content-secondary">请检查网络连接后重试</p>
        <button
          class="gemini-btn gemini-btn-primary mt-6"
          @click="loadNotebooks"
        >
          重试
        </button>
      </div>

      <div
        v-else-if="notebookStore.notebooks.length === 0"
        class="flex flex-col items-center justify-center rounded-glg border border-dashed border-line bg-surface-secondary py-20 text-center"
      >
        <div class="mb-4 flex h-12 w-12 items-center justify-center rounded-2xl border-2 border-dashed border-line text-content-secondary">
          <span class="text-xl font-light">+</span>
        </div>
        <p class="text-lg font-medium text-content">
          {{ emptyTitle }}
        </p>
        <p class="mt-2 text-sm text-content-secondary">{{ emptyHint }}</p>
        <button
          v-if="!favoriteOnly && !search"
          class="gemini-btn gemini-btn-primary mt-6"
          @click="showCreate = true"
        >
          创建笔记本
        </button>
      </div>

      <div v-else class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        <div
          v-for="nb in notebookStore.notebooks"
          :key="nb.id"
          class="group relative rounded-card border border-line bg-surface-elevated p-4 shadow-card-default transition-all hover:-translate-y-0.5 hover:border-primary/30 hover:shadow-card-hover"
        >
          <button
            class="gemini-btn gemini-btn-sm absolute right-4 top-4"
            :class="
              nb.is_favorite
                ? 'border-amber-400/10 bg-amber-400/15 text-amber-600 hover:bg-amber-400/20'
                : 'gemini-btn-ghost'
            "
            @click="handleToggleFavorite(nb.id)"
          >
            {{ nb.is_favorite ? '已收藏' : '收藏' }}
          </button>

          <router-link :to="`/app/notebook/${nb.id}`" class="block pr-20">
            <div class="mb-3 flex h-10 w-10 items-center justify-center rounded-gmd bg-primary-soft text-sm font-semibold text-primary">
              {{ (nb.name || 'N').charAt(0).toUpperCase() }}
            </div>
            <h3 class="font-medium text-content transition-colors group-hover:text-primary">
              {{ nb.name }}
            </h3>
            <p class="mt-2 line-clamp-2 text-sm text-content-secondary">
              {{ nb.description || '暂无描述' }}
            </p>
            <p class="mt-4 text-xs text-content-secondary">
              更新于 {{ formatDate(nb.updated_at) }}
            </p>
            <p class="mt-2 text-xs text-content-secondary">
              {{ nb.document_count || 0 }} 个文档
            </p>
          </router-link>
        </div>
      </div>
    </div>
  </div>

  <BaseModal v-model="showCreate" title="新建笔记本">
    <form class="mt-4 space-y-4" @submit.prevent="handleCreate">
      <BaseInput
        v-model="form.name"
        type="text"
        placeholder="笔记本名称"
        required
      />
      <textarea
        v-model="form.description"
        placeholder="描述（可选）"
        rows="3"
        class="w-full resize-none rounded-gmd border border-line bg-surface-secondary px-4 py-3 text-content outline-none transition-all placeholder:text-content-secondary focus:border-primary focus:bg-surface focus:ring-4 focus:ring-primary-soft"
      />
      <div class="flex justify-end gap-3">
        <BaseButton
          type="button"
          variant="ghost"
          @click="showCreate = false"
        >
          取消
        </BaseButton>
        <BaseButton
          type="submit"
          :disabled="creating"
        >
          {{ creating ? '创建中...' : '创建' }}
        </BaseButton>
      </div>
    </form>
  </BaseModal>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseInput from '@/components/ui/BaseInput.vue'
import BaseModal from '@/components/ui/BaseModal.vue'
import { useNotebookStore } from '@/stores/notebook'

const router = useRouter()
const notebookStore = useNotebookStore()

const showCreate = ref(false)
const creating = ref(false)
const search = ref('')
const favoriteOnly = ref(false)
const form = ref({ name: '', description: '' })
const loadError = ref(false)

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

async function loadNotebooks() {
  loadError.value = false
  try {
    await notebookStore.fetchNotebooks({
      search: search.value.trim() || undefined,
      is_favorite: favoriteOnly.value || undefined,
    })
  } catch {
    loadError.value = true
  }
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
    router.push(`/app/notebook/${notebook.id}`)
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
