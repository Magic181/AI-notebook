<template>
  <div class="flex min-h-screen items-center justify-center bg-surface-secondary px-4">
    <div class="gemini-rise w-full max-w-md rounded-2xl border border-line bg-surface-elevated p-8 shadow-gmd">
      <div class="mb-6 flex justify-center">
        <StarterLogo title="AI Notebook Kit" subtitle="Starter Demo" />
      </div>
      <h1 class="text-center text-xl font-semibold tracking-tight text-content">欢迎回来</h1>
      <p class="mt-1.5 text-center text-sm text-content-secondary">
        登录你的 AI 知识工作台
      </p>
      <form class="mt-6 space-y-4" @submit.prevent="handleLogin">
        <BaseInput
          v-model="username"
          type="text"
          placeholder="用户名"
          required
        />
        <BaseInput
          v-model="password"
          type="password"
          placeholder="密码"
          required
        />
        <BaseButton
          type="submit"
          :disabled="loading"
          full-width
        >
          {{ loading ? '登录中...' : '登录' }}
        </BaseButton>
      </form>
      <p class="mt-6 text-center text-sm text-content-secondary">
        还没有账号？
        <router-link to="/register" class="font-medium text-primary hover:underline">
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
import StarterLogo from '@/components/brand/StarterLogo.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseInput from '@/components/ui/BaseInput.vue'
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
    const redirect = (route.query.redirect as string) || '/app'
    router.push(redirect)
  } catch {
    // error shown by axios interceptor
  } finally {
    loading.value = false
  }
}
</script>
