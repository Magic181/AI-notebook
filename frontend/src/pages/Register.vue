<template>
  <div class="flex min-h-screen items-center justify-center bg-[var(--bg-secondary)]">
    <div class="w-full max-w-md rounded-2xl bg-[var(--bg)] p-8 shadow-sm">
      <h1 class="text-center text-xl font-semibold text-[var(--text)]">注册</h1>
      <p class="mt-2 text-center text-sm text-[var(--text-secondary)]">
        创建你的 AI 知识工作台账号
      </p>
      <form class="mt-6 space-y-4" @submit.prevent="handleRegister">
        <input
          v-model="username"
          type="text"
          placeholder="用户名"
          required
          class="w-full rounded-xl border border-[var(--border)] bg-[var(--bg)] px-4 py-3 text-[var(--text)] outline-none focus:border-[var(--primary)]"
        />
        <input
          v-model="email"
          type="email"
          placeholder="邮箱"
          required
          class="w-full rounded-xl border border-[var(--border)] bg-[var(--bg)] px-4 py-3 text-[var(--text)] outline-none focus:border-[var(--primary)]"
        />
        <input
          v-model="password"
          type="password"
          placeholder="密码"
          required
          minlength="6"
          class="w-full rounded-xl border border-[var(--border)] bg-[var(--bg)] px-4 py-3 text-[var(--text)] outline-none focus:border-[var(--primary)]"
        />
        <button
          type="submit"
          :disabled="loading"
          class="w-full rounded-xl bg-[var(--primary)] py-3 font-medium text-white transition-colors hover:bg-[var(--primary-hover)] disabled:opacity-50"
        >
          {{ loading ? '注册中...' : '注册' }}
        </button>
      </form>
      <p class="mt-4 text-center text-sm text-[var(--text-secondary)]">
        已有账号？
        <router-link to="/login" class="text-[var(--primary)] hover:underline">
          立即登录
        </router-link>
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { authApi } from '@/api/auth'

const router = useRouter()
const username = ref('')
const email = ref('')
const password = ref('')
const loading = ref(false)

async function handleRegister() {
  loading.value = true
  try {
    await authApi.register({
      username: username.value,
      email: email.value,
      password: password.value,
    })
    ElMessage.success('注册成功，请登录')
    router.push('/login')
  } catch {
    // error shown by axios interceptor
  } finally {
    loading.value = false
  }
}
</script>
