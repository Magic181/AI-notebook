import api from './index'

export interface Notebook {
  id: number
  name: string
  description: string
  created_at: string
  updated_at: string
  is_favorite: boolean
}

export const notebookApi = {
  list: () => api.get<Notebook[] | { items: Notebook[] }>('/notebooks/'),
  get: (id: number) => api.get<Notebook>(`/notebooks/${id}/`),
  create: (data: Partial<Notebook>) => api.post<Notebook>('/notebooks/', data),
  update: (id: number, data: Partial<Notebook>) =>
    api.put<Notebook>(`/notebooks/${id}/`, data),
  delete: (id: number) => api.delete(`/notebooks/${id}/`),
  toggleFavorite: (id: number) => api.post(`/notebooks/${id}/favorite/`),
}
