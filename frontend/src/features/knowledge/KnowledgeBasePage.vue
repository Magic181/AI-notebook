<template>
  <div class="flex h-full flex-col">
    <PageHeader
      eyebrow="Demo feature / Knowledge"
      title="Knowledge spaces"
      description="Notebook 是 Starter Kit 自带的示例业务容器；你可以把它替换成项目、客户、案件或任何自己的领域对象。"
    >
      <template #actions>
        <button class="kit-button kit-button-primary" @click="showCreate = true">
          <AppIcon name="plus" class="h-4 w-4" />
          新建空间
        </button>
      </template>
    </PageHeader>

    <div class="border-b border-line/80 bg-surface-elevated/75 px-4 py-3 backdrop-blur sm:px-6 lg:px-8">
      <div class="flex flex-col gap-3 sm:flex-row sm:items-center">
        <label class="relative min-w-0 flex-1">
          <span class="sr-only">搜索知识空间</span>
          <input
            v-model="search"
            type="search"
            placeholder="搜索名称或描述…"
            class="w-full rounded-xl border border-line bg-white px-4 py-2.5 text-sm text-content shadow-gsm outline-none transition placeholder:text-content-secondary focus:border-primary focus:ring-4 focus:ring-primary-soft"
          />
        </label>
        <button class="kit-button" :class="favoriteOnly ? 'kit-button-tonal' : 'kit-button-ghost'" @click="toggleFavoriteFilter">
          {{ favoriteOnly ? '显示全部' : '只看收藏' }}
        </button>
        <span class="font-mono text-[9px] uppercase tracking-[0.13em] text-content-secondary sm:ml-2">{{ notebookStore.notebooks.length }} spaces</span>
      </div>
    </div>

    <div class="min-h-0 flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8">
      <div v-if="notebookStore.loading" class="grid min-h-64 place-items-center border border-dashed border-line">
        <p class="font-mono text-[10px] uppercase tracking-[0.14em] text-content-secondary">Loading spaces…</p>
      </div>

      <div v-else-if="loadError" class="grid min-h-64 place-items-center rounded-xl border border-dashed border-line bg-surface-elevated p-8 text-center">
        <div>
          <p class="text-lg font-bold text-content">无法加载知识空间</p>
          <p class="mt-2 text-sm text-content-secondary">检查 API 服务后再试一次。</p>
          <button class="kit-button kit-button-primary mt-6" @click="loadNotebooks">重试</button>
        </div>
      </div>

      <div v-else-if="notebookStore.notebooks.length === 0" class="grid min-h-80 place-items-center rounded-xl border border-dashed border-line bg-surface-elevated p-8 text-center">
        <div class="max-w-sm">
          <span class="mx-auto grid h-12 w-12 place-items-center rounded-control bg-primary text-ink"><AppIcon name="plus" class="h-5 w-5" /></span>
          <p class="mt-5 text-xl font-bold tracking-[-0.035em] text-content">{{ emptyTitle }}</p>
          <p class="mt-2 text-sm leading-6 text-content-secondary">{{ emptyHint }}</p>
          <button v-if="!favoriteOnly && !search" class="kit-button kit-button-primary mt-6" @click="showCreate = true">创建第一个空间</button>
        </div>
      </div>

      <div v-else class="grid gap-4 md:grid-cols-2 2xl:grid-cols-3">
        <article v-for="(notebook, index) in notebookStore.notebooks" :key="notebook.id" class="group surface-card relative overflow-hidden transition hover:-translate-y-0.5 hover:border-primary/25 hover:shadow-card-hover">
          <div class="flex items-center justify-between px-5 pb-0 pt-5">
            <span class="text-[9px] font-semibold uppercase tracking-[0.1em] text-content-secondary">Space {{ String(index + 1).padStart(2, '0') }}</span>
            <button class="kit-button kit-button-sm" :class="notebook.is_favorite ? 'kit-button-tonal' : 'kit-button-ghost'" @click="handleToggleFavorite(notebook.id)">
              {{ notebook.is_favorite ? '已收藏' : '收藏' }}
            </button>
          </div>
          <RouterLink :to="`/app/notebook/${notebook.id}`" class="block px-5 pb-5 pt-3">
            <div class="flex items-start justify-between gap-4">
              <span class="grid h-11 w-11 shrink-0 place-items-center rounded-xl bg-primary-soft text-xs font-bold uppercase text-primary">{{ (notebook.name || 'N').charAt(0) }}</span>
              <AppIcon name="arrow-up-right" class="h-5 w-5 text-content-secondary transition group-hover:text-primary" />
            </div>
            <h2 class="mt-6 truncate text-xl font-[680] tracking-[-0.035em] text-content">{{ notebook.name }}</h2>
            <p class="mt-2 line-clamp-2 min-h-10 text-sm leading-5 text-content-secondary">{{ notebook.description || '未填写描述。这个空间可以用来演示文档摄取与 RAG 对话。' }}</p>
            <div class="mt-6 flex items-center justify-between border-t border-line pt-4 text-[10px] font-medium uppercase tracking-[0.07em] text-content-secondary">
              <span>{{ notebook.document_count || 0 }} documents</span>
              <span>{{ formatDate(notebook.updated_at) }}</span>
            </div>
          </RouterLink>
        </article>
      </div>
    </div>
  </div>

  <BaseModal v-model="showCreate" title="新建知识空间">
    <form class="mt-5 space-y-4" @submit.prevent="handleCreate">
      <label class="block">
        <span class="mb-2 block font-mono text-[10px] font-bold uppercase tracking-[0.12em] text-content-secondary">Name</span>
        <BaseInput v-model="form.name" type="text" placeholder="例如：产品研究" required />
      </label>
      <label class="block">
        <span class="mb-2 block font-mono text-[10px] font-bold uppercase tracking-[0.12em] text-content-secondary">Description</span>
        <textarea v-model="form.description" placeholder="这个空间会装什么内容？" rows="3" class="w-full resize-none rounded-control border border-line bg-surface-elevated px-4 py-3 text-content outline-none transition placeholder:text-content-secondary focus:border-primary focus:ring-4 focus:ring-primary-soft" />
      </label>
      <div class="flex justify-end gap-3 pt-2">
        <BaseButton type="button" variant="ghost" @click="showCreate = false">取消</BaseButton>
        <BaseButton type="submit" :disabled="creating">{{ creating ? '创建中…' : '创建空间' }}</BaseButton>
      </div>
    </form>
  </BaseModal>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import AppIcon from '@/components/ui/AppIcon.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseInput from '@/components/ui/BaseInput.vue'
import BaseModal from '@/components/ui/BaseModal.vue'
import PageHeader from '@/components/ui/PageHeader.vue'
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
  if (favoriteOnly.value) return '还没有收藏的空间'
  if (search.value.trim()) return '没有匹配结果'
  return '从一个空空间开始'
})

const emptyHint = computed(() => (favoriteOnly.value || search.value.trim() ? '调整筛选条件，或者返回全部空间。' : '创建空间、上传文档，然后验证完整的摄取与问答链路。'))

function formatDate(value: string) {
  return new Intl.DateTimeFormat('zh-CN', { month: 'short', day: 'numeric' }).format(new Date(value))
}

async function loadNotebooks() {
  loadError.value = false
  try {
    await notebookStore.fetchNotebooks({ search: search.value.trim() || undefined, is_favorite: favoriteOnly.value || undefined })
  } catch {
    loadError.value = true
  }
}

function toggleFavoriteFilter() {
  favoriteOnly.value = !favoriteOnly.value
  void loadNotebooks()
}

async function handleToggleFavorite(id: number) {
  try {
    await notebookStore.toggleFavorite(id)
  } catch {
    // The API interceptor presents the request error.
  }
}

async function handleCreate() {
  if (!form.value.name.trim()) return
  creating.value = true
  try {
    const notebook = await notebookStore.createNotebook({ name: form.value.name.trim(), description: form.value.description.trim() })
    showCreate.value = false
    form.value = { name: '', description: '' }
    ElMessage.success('空间已创建')
    await router.push(`/app/notebook/${notebook.id}`)
  } catch {
    // The API interceptor presents the request error.
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
