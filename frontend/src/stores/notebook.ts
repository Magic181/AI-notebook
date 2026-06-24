import { defineStore } from 'pinia'
import { ref } from 'vue'
import {
  notebookApi,
  type Notebook,
  type NotebookListParams,
} from '@/api/notebook'

export const useNotebookStore = defineStore('notebook', () => {
  const notebooks = ref<Notebook[]>([])
  const currentNotebook = ref<Notebook | null>(null)
  const loading = ref(false)
  const total = ref(0)
  const filters = ref<NotebookListParams>({})

  function syncNotebookInList(notebook: Notebook) {
    const index = notebooks.value.findIndex((item) => item.id === notebook.id)
    if (index >= 0) {
      notebooks.value[index] = notebook
    }
    if (currentNotebook.value?.id === notebook.id) {
      currentNotebook.value = notebook
    }
  }

  function removeNotebookFromList(id: number) {
    notebooks.value = notebooks.value.filter((item) => item.id !== id)
    if (currentNotebook.value?.id === id) {
      currentNotebook.value = null
    }
  }

  async function fetchNotebooks(params?: NotebookListParams) {
    loading.value = true
    if (params) {
      filters.value = { ...filters.value, ...params }
    }
    try {
      const { data } = await notebookApi.list(filters.value)
      notebooks.value = data.items
      total.value = data.total
    } finally {
      loading.value = false
    }
  }

  async function fetchNotebook(id: number) {
    const { data } = await notebookApi.get(id)
    currentNotebook.value = data
    syncNotebookInList(data)
    return data
  }

  async function createNotebook(payload: Partial<Notebook>) {
    const { data } = await notebookApi.create(payload)
    notebooks.value.unshift(data)
    total.value += 1
    return data
  }

  async function updateNotebook(id: number, payload: Partial<Notebook>) {
    const { data } = await notebookApi.update(id, payload)
    syncNotebookInList(data)
    return data
  }

  async function deleteNotebook(id: number) {
    await notebookApi.delete(id)
    removeNotebookFromList(id)
    total.value = Math.max(0, total.value - 1)
  }

  async function toggleFavorite(id: number) {
    const { data } = await notebookApi.toggleFavorite(id)
    syncNotebookInList(data)
    if (filters.value.is_favorite && !data.is_favorite) {
      notebooks.value = notebooks.value.filter((item) => item.id !== id)
      total.value = Math.max(0, total.value - 1)
    }
    return data
  }

  return {
    notebooks,
    currentNotebook,
    loading,
    total,
    filters,
    fetchNotebooks,
    fetchNotebook,
    createNotebook,
    updateNotebook,
    deleteNotebook,
    toggleFavorite,
  }
})
