import api from './index'

export type DocumentStatus = 'uploading' | 'parsing' | 'completed' | 'failed'

export interface Document {
  id: number
  notebook_id: number
  name: string
  file_type: string
  file_size: number
  status: DocumentStatus
  chunk_count: number
  asset_count: number
  error_message?: string
  created_at: string
  updated_at: string
}

export const documentApi = {
  list: (notebookId: number) =>
    api.get<Document[]>(`/notebooks/${notebookId}/documents/`),
  upload: (notebookId: number, files: File[]) => {
    const formData = new FormData()
    files.forEach((file) => formData.append('files', file))
    return api.post<Document[]>(`/notebooks/${notebookId}/documents/`, formData)
  },
  get: (id: number) => api.get<Document>(`/documents/${id}/`),
  delete: (id: number) => api.delete(`/documents/${id}/`),
}
