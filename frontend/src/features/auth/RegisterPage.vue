<template>
  <AuthLayout eyebrow="Account / Register" title="创建 Demo 账号。" description="用最小信息进入工作区。这里是认证模块示例，不绑定任何商业身份系统。">
    <form class="space-y-5" @submit.prevent="handleRegister">
      <label class="block"><span class="mb-2 block font-mono text-[10px] font-bold uppercase tracking-[0.12em] text-content-secondary">Username</span><BaseInput v-model="username" type="text" placeholder="选择用户名" autocomplete="username" required /></label>
      <label class="block"><span class="mb-2 block font-mono text-[10px] font-bold uppercase tracking-[0.12em] text-content-secondary">Email</span><BaseInput v-model="email" type="email" placeholder="you@example.com" autocomplete="email" required /></label>
      <label class="block"><span class="mb-2 block font-mono text-[10px] font-bold uppercase tracking-[0.12em] text-content-secondary">Password</span><BaseInput v-model="password" type="password" placeholder="至少 6 位" autocomplete="new-password" required minlength="6" /></label>
      <BaseButton type="submit" :disabled="loading" full-width>{{ loading ? '正在创建…' : '创建并进入' }}<AppIcon v-if="!loading" name="arrow-up-right" class="h-4 w-4" /></BaseButton>
    </form>
    <p class="mt-7 border-t border-line pt-5 text-sm text-content-secondary">已经有账号？ <RouterLink to="/login" class="font-semibold text-content underline decoration-primary decoration-2 underline-offset-4">直接登录</RouterLink></p>
  </AuthLayout>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import AppIcon from '@/components/ui/AppIcon.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseInput from '@/components/ui/BaseInput.vue'
import { useUserStore } from '@/stores/user'
import AuthLayout from './AuthLayout.vue'

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
    await router.push('/app')
  } catch {
    // The API interceptor presents the request error.
  } finally {
    loading.value = false
  }
}
</script>
