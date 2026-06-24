<template>
  <div class="flex h-screen bg-[var(--bg)]">
    <aside
      class="flex flex-col border-r border-[var(--border)] bg-[var(--bg-secondary)] transition-all"
      :class="uiStore.sidebarCollapsed ? 'w-16' : 'w-64'"
    >
      <div class="flex h-14 items-center justify-between border-b border-[var(--border)] px-4">
        <router-link
          v-if="!uiStore.sidebarCollapsed"
          to="/"
          class="text-lg font-semibold text-[var(--primary)]"
        >
          AI Notebook
        </router-link>
        <button
          class="rounded-lg p-2 text-[var(--text-secondary)] hover:bg-[var(--border)]"
          @click="uiStore.toggleSidebar()"
        >
          ☰
        </button>
      </div>

      <nav class="flex-1 overflow-y-auto p-3">
        <router-link
          to="/"
          class="mb-1 flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm transition-colors"
          :class="isActive('/') ? 'bg-[var(--primary)]/10 text-[var(--primary)]' : 'text-[var(--text-secondary)] hover:bg-[var(--border)]'"
        >
          <span>📚</span>
          <span v-if="!uiStore.sidebarCollapsed">我的笔记本</span>
        </router-link>

        <div v-if="!uiStore.sidebarCollapsed" class="mt-4 px-3">
          <p class="mb-2 text-xs font-medium uppercase tracking-wide text-[var(--text-secondary)]">
            最近
          </p>
          <router-link
            v-for="nb in notebookStore.notebooks.slice(0, 8)"
            :key="nb.id"
            :to="`/notebook/${nb.id}`"
            class="mb-1 block truncate rounded-lg px-2 py-1.5 text-sm text-[var(--text-secondary)] hover:bg-[var(--border)] hover:text-[var(--text)]"
          >
            {{ nb.name }}
          </router-link>
        </div>
      </nav>

      <div class="border-t border-[var(--border)] p-3">
        <button
          class="mb-2 flex w-full items-center gap-3 rounded-xl px-3 py-2 text-sm text-[var(--text-secondary)] hover:bg-[var(--border)]"
          @click="uiStore.toggleDarkMode()"
        >
          <span>{{ uiStore.darkMode ? '☀️' : '🌙' }}</span>
          <span v-if="!uiStore.sidebarCollapsed">{{ uiStore.darkMode ? '浅色模式' : '深色模式' }}</span>
        </button>
        <button
          class="flex w-full items-center gap-3 rounded-xl px-3 py-2 text-sm text-[var(--text-secondary)] hover:bg-[var(--border)]"
          @click="handleLogout"
        >
          <span>🚪</span>
          <span v-if="!uiStore.sidebarCollapsed">退出登录</span>
        </button>
      </div>
    </aside>

    <main class="flex flex-1 flex-col overflow-hidden">
      <router-view />
    </main>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUIStore } from '@/stores/ui'
import { useNotebookStore } from '@/stores/notebook'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const uiStore = useUIStore()
const notebookStore = useNotebookStore()
const userStore = useUserStore()

function isActive(path: string) {
  return route.path === path
}

function handleLogout() {
  userStore.logout()
  router.push('/login')
}

onMounted(() => {
  notebookStore.fetchNotebooks().catch(() => {})
})
</script>
