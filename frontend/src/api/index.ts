import axios, { type AxiosError, type InternalAxiosRequestConfig } from 'axios'
import { ElMessage } from 'element-plus'
import { isTokenExpiringSoon } from '@/utils/jwt'

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

interface ApiBody<T = unknown> {
  code: number
  message: string
  data: T
  errors?: Array<{ field: string; message: string }>
}

let refreshPromise: Promise<string> | null = null
let skipAuthRedirect = false

function saveTokens(access: string, refresh?: string) {
  localStorage.setItem('access_token', access)
  if (refresh) {
    localStorage.setItem('refresh_token', refresh)
  }
}

function clearTokens() {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
}

function redirectToLogin() {
  clearTokens()
  if (!skipAuthRedirect && !window.location.pathname.startsWith('/login')) {
    window.location.href = '/login'
  }
}

export function runWithoutAuthRedirect<T>(fn: () => Promise<T>): Promise<T> {
  skipAuthRedirect = true
  return fn().finally(() => {
    skipAuthRedirect = false
  })
}

async function refreshAccessToken(): Promise<string> {
  const refresh = localStorage.getItem('refresh_token')
  if (!refresh) {
    redirectToLogin()
    throw new Error('No refresh token')
  }

  const response = await axios.post(
    '/api/v1/auth/refresh/',
    { refresh },
    { headers: { 'Content-Type': 'application/json' } },
  )
  const body = response.data as ApiBody<{ access: string; refresh?: string }>
  const data = body?.data ?? response.data
  saveTokens(data.access, data.refresh)
  return data.access
}

async function ensureFreshToken(): Promise<void> {
  const access = localStorage.getItem('access_token')
  if (!access || !isTokenExpiringSoon(access)) return

  if (!refreshPromise) {
    refreshPromise = refreshAccessToken().finally(() => {
      refreshPromise = null
    })
  }
  await refreshPromise
}

api.interceptors.request.use(async (config) => {
  const url = config.url ?? ''
  const isAuthEndpoint =
    url.includes('/auth/refresh/') ||
    url.includes('/auth/login/') ||
    url.includes('/auth/register/') ||
    url.includes('/auth/logout/')

  if (!isAuthEndpoint) {
    await ensureFreshToken().catch(() => {})
  }

  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => {
    if (response.status === 204) {
      return response
    }
    const body = response.data as ApiBody
    if (body && typeof body === 'object' && 'code' in body && 'data' in body) {
      if (body.code >= 400) {
        return Promise.reject(new Error(body.message || 'Request failed'))
      }
      response.data = body.data
    }
    return response
  },
  async (error: AxiosError<ApiBody>) => {
    const status = error.response?.status
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean }
    const message =
      error.response?.data?.message ||
      error.message ||
      'Network error'

    const isAuthEndpoint =
      originalRequest?.url?.includes('/auth/login/') ||
      originalRequest?.url?.includes('/auth/register/') ||
      originalRequest?.url?.includes('/auth/refresh/') ||
      originalRequest?.url?.includes('/auth/me/')

    if (status === 401 && originalRequest && !originalRequest._retry && !isAuthEndpoint) {
      originalRequest._retry = true
      try {
        if (!refreshPromise) {
          refreshPromise = refreshAccessToken().finally(() => {
            refreshPromise = null
          })
        }
        const access = await refreshPromise
        originalRequest.headers.Authorization = `Bearer ${access}`
        return api(originalRequest)
      } catch {
        redirectToLogin()
        return Promise.reject(error)
      }
    }

    if (status === 401 && !skipAuthRedirect) {
      redirectToLogin()
    } else if (status !== 401) {
      ElMessage.error(message)
    }

    return Promise.reject(error)
  },
)

export default api
export { saveTokens, clearTokens }
