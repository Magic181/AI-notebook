<template>
  <div class="flex min-h-screen items-center justify-center bg-[var(--bg-secondary)]">
    <div class="w-full max-w-md rounded-2xl bg-[var(--bg)] p-8 shadow-sm">
      <h1 class="text-center text-xl font-semibold text-[var(--text)]">登录</h1>
      <p class="mt-2 text-center text-sm text-[var(--text-secondary)]">
        登录你的 AI 知识工作台
      </p>
      <form class="mt-6 space-y-4" @submit.prevent="handleLogin">
        <input
          v-model="username"
          type="text"
          placeholder="用户名"
          required
          class="w-full rounded-xl border border-[var(--border)] bg-[var(--bg)] px-4 py-3 text-[var(--text)] outline-none focus:border-[var(--primary)]"
        />
        <input
          v-model="password"
          type="password"
          placeholder="密码"
          required
          class="w-full rounded-xl border border-[var(--border)] bg-[var(--bg)] px-4 py-3 text-[var(--text)] outline-none focus:border-[var(--primary)]"
        />
        <button
          type="submit"
          :disabled="loading"
          class="w-full rounded-xl bg-[var(--primary)] py-3 font-medium text-white transition-colors hover:bg-[var(--primary-hover)] disabled:opacity-50"
        >
          {{ loading ? '登录中...' : '登录' }}
        </button>
      </form>
      <p class="mt-4 text-center text-sm text-[var(--text-secondary)]">
        还没有账号？
        <router-link to="/register" class="text-[var(--primary)] hover:underline">
          立即注册
        </router-link>
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const username = ref('')
const password = ref('')
const loading = ref(false)

async function handleLogin() {
  loading.value = true
  try {
    await userStore.login(username.value, password.value)
    ElMessage.success('登录成功')
    const redirect = (route.query.redirect as string) || '/'
    router.push(redirect)
  } catch {
    // error shown by axios interceptor
  } finally {
    loading.value = false
  }
}
</script>
