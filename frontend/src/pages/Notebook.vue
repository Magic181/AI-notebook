<template>
  <div class="flex h-full flex-col">
    <header class="flex min-h-16 shrink-0 flex-col gap-3 px-6 py-3 md:flex-row md:items-center md:justify-between">
      <div class="min-w-0 flex-1">
        <h2 class="truncate text-lg font-semibold tracking-tight text-content">
          {{ notebook?.name || 'Notebook' }}
        </h2>
        <p v-if="notebook?.description" class="truncate text-sm text-content-secondary">
          {{ notebook.description }}
        </p>
      </div>
      <div v-if="notebook" class="flex w-full flex-wrap items-center gap-2 md:ml-4 md:w-auto md:shrink-0 md:justify-end">
        <button
          class="gemini-btn gemini-btn-sm"
          :class="
            notebook.is_favorite
              ? 'border-amber-400/10 bg-amber-400/15 text-amber-600 hover:bg-amber-400/20'
              : 'gemini-btn-ghost'
          "
          @click="handleToggleFavorite"
        >
          {{ notebook.is_favorite ? '已收藏' : '收藏' }}
        </button>
        <button
          class="gemini-btn gemini-btn-ghost gemini-btn-sm"
          @click="showEdit = true"
        >
          编辑
        </button>
        <button
          class="gemini-btn gemini-btn-danger gemini-btn-sm"
          @click="showDelete = true"
        >
          删除
        </button>
        <router-link
          :to="`/app/chat/${notebook.id}`"
          class="gemini-btn gemini-btn-primary gemini-btn-sm"
        >
          开始对话
        </router-link>
      </div>
    </header>

    <div class="flex-1 overflow-y-auto p-6">
      <div v-if="loading" class="flex items-center justify-center py-20">
        <p class="text-content-secondary">加载中...</p>
      </div>
      <div
        v-else-if="!notebook"
        class="flex flex-col items-center justify-center py-20 text-content-secondary"
      >
        <p>笔记本不存在或无权访问</p>
        <router-link to="/app" class="mt-4 font-medium text-primary hover:underline">
          返回首页
        </router-link>
      </div>
      <div v-else class="space-y-6">
        <UploadZone
          :uploading="documentStore.uploading"
          @upload="handleUpload"
        />
        <DocumentList
          :documents="documentStore.documents"
          :loading="documentStore.loading"
          :reparsing-ids="reparsingDocumentIds"
          @delete="openDeleteDocument"
          @reparse="handleReparseDocument"
        />
      </div>
    </div>
  </div>

  <BaseModal v-if="notebook" v-model="showEdit" title="编辑笔记本">
    <form class="mt-4 space-y-4" @submit.prevent="handleUpdate">
      <BaseInput
        v-model="editForm.name"
        type="text"
        placeholder="笔记本名称"
        required
      />
      <textarea
        v-model="editForm.description"
        placeholder="描述（可选）"
        rows="3"
        class="w-full resize-none rounded-gmd border border-line bg-surface-secondary px-4 py-3 text-content outline-none transition-all placeholder:text-content-secondary focus:border-primary focus:bg-surface focus:ring-4 focus:ring-primary-soft"
      />
      <div class="flex justify-end gap-3">
        <BaseButton
          type="button"
          variant="ghost"
          @click="showEdit = false"
        >
          取消
        </BaseButton>
        <BaseButton
          type="submit"
          :disabled="saving"
        >
          {{ saving ? '保存中...' : '保存' }}
        </BaseButton>
      </div>
    </form>
  </BaseModal>

  <BaseModal v-if="notebook" v-model="showDelete" title="确认删除" max-width="sm">
    <p class="mt-2 text-sm text-content-secondary">
      确定要删除「{{ notebook.name }}」吗？此操作不可恢复。
    </p>
    <template #footer>
      <BaseButton variant="ghost" @click="showDelete = false">
        取消
      </BaseButton>
      <BaseButton
        variant="danger"
        :disabled="deleting"
        @click="handleDelete"
      >
        {{ deleting ? '删除中...' : '删除' }}
      </BaseButton>
    </template>
  </BaseModal>

  <BaseModal v-model="showDeleteDocument" title="确认删除文档" max-width="sm">
    <p class="mt-2 break-words text-sm text-content-secondary">
      确定要删除「{{ documentToDelete?.name }}」吗？此操作不可恢复。
    </p>
    <template #footer>
      <BaseButton variant="ghost" @click="showDeleteDocument = false">
        取消
      </BaseButton>
      <BaseButton
        variant="danger"
        :disabled="deletingDocument"
        @click="handleDeleteDocument"
      >
        {{ deletingDocument ? '删除中...' : '删除' }}
      </BaseButton>
    </template>
  </BaseModal>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { Document } from '@/api/document'
import DocumentList from '@/components/document/DocumentList.vue'
import UploadZone from '@/components/document/UploadZone.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseInput from '@/components/ui/BaseInput.vue'
import BaseModal from '@/components/ui/BaseModal.vue'
import { useDocumentStore } from '@/stores/document'
import { useNotebookStore } from '@/stores/notebook'

const route = useRoute()
const router = useRouter()
const notebookStore = useNotebookStore()
const documentStore = useDocumentStore()

const loading = ref(false)
const showEdit = ref(false)
const showDelete = ref(false)
const showDeleteDocument = ref(false)
const saving = ref(false)
const deleting = ref(false)
const deletingDocument = ref(false)
const documentToDelete = ref<Document | null>(null)
const editForm = ref({ name: '', description: '' })
const reparsingDocumentIds = ref<number[]>([])

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
    await documentStore.fetchDocuments(id)
  } catch {
    notebookStore.currentNotebook = null
  } finally {
    loading.value = false
  }
}

async function handleUpload(files: File[]) {
  if (!notebook.value || files.length === 0) return
  try {
    await documentStore.uploadDocuments(notebook.value.id, files)
    await notebookStore.fetchNotebook(notebook.value.id)
    ElMessage.success(`已上传 ${files.length} 个文件`)
  } catch {
    // error shown by axios interceptor
  }
}

function openDeleteDocument(document: Document) {
  documentToDelete.value = document
  showDeleteDocument.value = true
}

async function handleDeleteDocument() {
  if (!documentToDelete.value || !notebook.value) return
  deletingDocument.value = true
  try {
    await documentStore.deleteDocument(documentToDelete.value.id)
    await notebookStore.fetchNotebook(notebook.value.id)
    showDeleteDocument.value = false
    documentToDelete.value = null
    ElMessage.success('文档已删除')
  } catch {
    // error shown by axios interceptor
  } finally {
    deletingDocument.value = false
  }
}

async function handleReparseDocument(document: Document) {
  if (!notebook.value || reparsingDocumentIds.value.includes(document.id)) return
  reparsingDocumentIds.value = [...reparsingDocumentIds.value, document.id]
  try {
    await documentStore.reparseDocument(notebook.value.id, document.id)
    await notebookStore.fetchNotebook(notebook.value.id)
    ElMessage.success('已重新解析，稍后会刷新处理结果')
  } catch {
    // error shown by axios interceptor
  } finally {
    reparsingDocumentIds.value = reparsingDocumentIds.value.filter((id) => id !== document.id)
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
    router.push('/app')
  } catch {
    // error shown by axios interceptor
  } finally {
    deleting.value = false
  }
}

onMounted(loadNotebook)
watch(() => route.params.id, loadNotebook)
onUnmounted(() => documentStore.reset())
</script>
