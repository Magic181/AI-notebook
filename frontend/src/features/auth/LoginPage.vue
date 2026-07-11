<template>
  <AuthLayout eyebrow="Account / Login" title="欢迎回来。" description="登录 Demo 工作区，查看 Starter Kit 的真实知识摄取与 RAG 对话流程。">
    <form class="space-y-5" @submit.prevent="handleLogin">
      <label class="block"><span class="mb-2 block font-mono text-[10px] font-bold uppercase tracking-[0.12em] text-content-secondary">Username</span><BaseInput v-model="username" type="text" placeholder="输入用户名" autocomplete="username" required /></label>
      <label class="block"><span class="mb-2 block font-mono text-[10px] font-bold uppercase tracking-[0.12em] text-content-secondary">Password</span><BaseInput v-model="password" type="password" placeholder="输入密码" autocomplete="current-password" required /></label>
      <BaseButton type="submit" :disabled="loading" full-width>{{ loading ? '正在登录…' : '进入工作台' }}<AppIcon v-if="!loading" name="arrow-up-right" class="h-4 w-4" /></BaseButton>
    </form>
    <p class="mt-7 border-t border-line pt-5 text-sm text-content-secondary">还没有 Demo 账号？ <RouterLink to="/register" class="font-semibold text-content underline decoration-primary decoration-2 underline-offset-4">创建一个</RouterLink></p>
  </AuthLayout>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import AppIcon from '@/components/ui/AppIcon.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseInput from '@/components/ui/BaseInput.vue'
import { useUserStore } from '@/stores/user'
import AuthLayout from './AuthLayout.vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const username = ref('')
const password = ref('')
const loading = ref(false)

async function handleLogin() {
  loading.value = true
  try {
    await userStore.login(username.value, password.value)
    ElMessage.success('登录成功')
    await router.push((route.query.redirect as string) || '/app')
  } catch {
    // The API interceptor presents the request error.
  } finally {
    loading.value = false
  }
}
</script>
