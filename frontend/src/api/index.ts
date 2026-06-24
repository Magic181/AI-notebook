import axios, { type AxiosError } from 'axios'
import { ElMessage } from 'element-plus'

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

interface ApiBody<T = unknown> {
  code: number
  message: string
  data: T
  errors?: Array<{ field: string; message: string }>
}

api.interceptors.response.use(
  (response) => {
    const body = response.data as ApiBody
    if (body && typeof body === 'object' && 'code' in body && 'data' in body) {
      if (body.code >= 400) {
        return Promise.reject(new Error(body.message || 'Request failed'))
      }
      response.data = body.data
    }
    return response
  },
  (error: AxiosError<ApiBody>) => {
    const status = error.response?.status
    const message =
      error.response?.data?.message ||
      error.message ||
      'Network error'

    if (status === 401) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      if (!window.location.pathname.startsWith('/login')) {
        window.location.href = '/login'
      }
    } else if (status !== 401) {
      ElMessage.error(message)
    }

    return Promise.reject(error)
  },
)

export default api
