import { defineStore } from 'pinia'
import { ref } from 'vue'
import { authApi, type UserProfile } from '@/api/auth'
import { clearTokens, runWithoutAuthRedirect, saveTokens } from '@/api/index'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('access_token') || '')
  const profile = ref<UserProfile | null>(null)
  const isLoggedIn = ref(false)
  const authReady = ref(false)

  function setAuth(access: string, refresh: string) {
    token.value = access
    isLoggedIn.value = true
    saveTokens(access, refresh)
  }

  function clearAuth() {
    token.value = ''
    profile.value = null
    isLoggedIn.value = false
    clearTokens()
  }

  async function fetchProfile() {
    const { data } = await authApi.me()
    profile.value = data
    isLoggedIn.value = true
    return data
  }

  async function initAuth() {
    if (!token.value) {
      authReady.value = true
      return false
    }

    try {
      await runWithoutAuthRedirect(() => fetchProfile())
      return true
    } catch {
      clearAuth()
      return false
    } finally {
      authReady.value = true
    }
  }

  async function login(username: string, password: string) {
    const { data } = await authApi.login({ username, password })
    setAuth(data.access, data.refresh)
    await fetchProfile()
  }

  async function register(username: string, email: string, password: string) {
    const { data } = await authApi.register({ username, email, password })
    setAuth(data.access, data.refresh)
    await fetchProfile()
  }

  async function logout() {
    const refresh = localStorage.getItem('refresh_token')
    try {
      if (refresh) {
        await authApi.logout(refresh)
      }
    } catch {
      // token may already be invalid
    } finally {
      clearAuth()
    }
  }

  return {
    token,
    profile,
    isLoggedIn,
    authReady,
    login,
    register,
    logout,
    fetchProfile,
    initAuth,
    setAuth,
  }
})
