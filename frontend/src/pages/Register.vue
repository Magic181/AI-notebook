<template>
  <div class="flex min-h-screen items-center justify-center bg-surface-secondary px-4">
    <div class="gemini-rise w-full max-w-md rounded-2xl border border-line bg-surface-elevated p-8 shadow-gmd">
      <div class="mb-6 flex justify-center">
        <StarterLogo title="AI Notebook Kit" subtitle="Starter Demo" />
      </div>
      <h1 class="text-center text-xl font-semibold tracking-tight text-content">创建账号</h1>
      <p class="mt-1.5 text-center text-sm text-content-secondary">
        创建你的 AI 知识工作台账号
      </p>
      <form class="mt-6 space-y-4" @submit.prevent="handleRegister">
        <BaseInput
          v-model="username"
          type="text"
          placeholder="用户名"
          required
        />
        <BaseInput
          v-model="email"
          type="email"
          placeholder="邮箱"
          required
        />
        <BaseInput
          v-model="password"
          type="password"
          placeholder="密码（至少 6 位）"
          required
          minlength="6"
        />
        <BaseButton
          type="submit"
          :disabled="loading"
          full-width
        >
          {{ loading ? '注册中...' : '注册' }}
        </BaseButton>
      </form>
      <p class="mt-6 text-center text-sm text-content-secondary">
        已有账号？
        <router-link to="/login" class="font-medium text-primary hover:underline">
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
import StarterLogo from '@/components/brand/StarterLogo.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseInput from '@/components/ui/BaseInput.vue'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()
const username = ref('')
const email = ref('')
const password = ref('')
const loading = ref(false)

async function handleRegister() {
  loading.value = true
  try {
    await userStore.register(username.value, email.value, password.value)
    ElMessage.success('注册成功')
    router.push('/app')
  } catch {
    // error shown by axios interceptor
  } finally {
    loading.value = false
  }
}
</script>
