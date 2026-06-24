<template>
  <div class="flex h-screen bg-[var(--bg)]">
    <aside
      class="border-r border-[var(--border)] bg-[var(--bg-secondary)] flex flex-col transition-all duration-200"
      :class="sidebarCollapsed ? 'w-16' : 'w-64'"
    >
      <div class="p-4 border-b border-[var(--border)] flex items-center justify-between">
        <router-link
          v-if="!sidebarCollapsed"
          to="/"
          class="text-lg font-semibold text-[var(--primary)] hover:opacity-80"
        >
          AI Notebook
        </router-link>
        <button
          class="p-1.5 rounded-lg hover:bg-[var(--border)] text-[var(--text-secondary)]"
          @click="uiStore.toggleSidebar()"
        >
          <el-icon><Fold v-if="!sidebarCollapsed" /><Expand v-else /></el-icon>
        </button>
      </div>

      <nav class="flex-1 p-3 overflow-y-auto space-y-1">
        <router-link
          to="/"
          class="flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm transition-colors"
          :class="isActive('/') ? 'bg-[var(--primary)]/10 text-[var(--primary)]' : 'text-[var(--text-secondary)] hover:bg-[var(--border)]/50'"
        >
          <el-icon><Collection /></el-icon>
          <span v-if="!sidebarCollapsed">Notebooks</span>
        </router-link>
      </nav>

      <div class="p-3 border-t border-[var(--border)] space-y-1">
        <button
          class="flex items-center gap-3 w-full px-3 py-2.5 rounded-xl text-sm text-[var(--text-secondary)] hover:bg-[var(--border)]/50 transition-colors"
          @click="uiStore.toggleDarkMode()"
        >
          <el-icon><Moon v-if="!uiStore.darkMode" /><Sunny v-else /></el-icon>
          <span v-if="!sidebarCollapsed">{{ uiStore.darkMode ? 'Light' : 'Dark' }}</span>
        </button>
        <button
          class="flex items-center gap-3 w-full px-3 py-2.5 rounded-xl text-sm text-[var(--text-secondary)] hover:bg-[var(--border)]/50 transition-colors"
          @click="handleLogout"
        >
          <el-icon><SwitchButton /></el-icon>
          <span v-if="!sidebarCollapsed">Logout</span>
        </button>
      </div>
    </aside>

    <div class="flex-1 flex flex-col min-w-0">
      <header
        v-if="title"
        class="h-14 border-b border-[var(--border)] flex items-center px-6 shrink-0"
      >
        <h2 class="font-medium text-[var(--text)]">{{ title }}</h2>
      </header>
      <main
        class="flex-1 min-h-0"
        :class="fill ? 'flex flex-col overflow-hidden' : 'overflow-y-auto'"
      >
        <slot />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { Collection, Expand, Fold, Moon, Sunny, SwitchButton } from '@element-plus/icons-vue'
import { useUIStore } from '@/stores/ui'
import { useUserStore } from '@/stores/user'

defineProps<{
  title?: string
  fill?: boolean
}>()

const route = useRoute()
const router = useRouter()
const uiStore = useUIStore()
const userStore = useUserStore()
const { sidebarCollapsed } = storeToRefs(uiStore)

function isActive(path: string) {
  return route.path === path
}

function handleLogout() {
  userStore.logout()
  router.push('/login')
}
</script>
