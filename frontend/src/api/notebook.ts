import api from './index'

export interface Notebook {
  id: number
  name: string
  description: string
  created_at: string
  updated_at: string
  is_favorite: boolean
  document_count?: number
}

export interface NotebookListParams {
  search?: string
  is_favorite?: boolean
  page?: number
  page_size?: number
  ordering?: string
}

export interface NotebookListResponse {
  items: Notebook[]
  total: number
  page: number
  page_size: number
}

export const notebookApi = {
  list: (params?: NotebookListParams) =>
    api.get<NotebookListResponse>('/notebooks/', { params }),
  get: (id: number) => api.get<Notebook>(`/notebooks/${id}/`),
  create: (data: Partial<Notebook>) => api.post<Notebook>('/notebooks/', data),
  update: (id: number, data: Partial<Notebook>) =>
    api.patch<Notebook>(`/notebooks/${id}/`, data),
  delete: (id: number) => api.delete(`/notebooks/${id}/`),
  toggleFavorite: (id: number) => api.post<Notebook>(`/notebooks/${id}/favorite/`),
}
