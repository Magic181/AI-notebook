<template>
  <div class="flex h-screen gap-2 bg-surface p-2">
    <div
      v-if="uiStore.mobileSidebarOpen"
      class="fixed inset-0 z-30 bg-black/40 md:hidden"
      @click="uiStore.closeMobileSidebar()"
    />

    <aside
      class="fixed inset-y-2 left-2 z-40 w-64 flex flex-col rounded-2xl bg-surface-elevated shadow-gsm transition-transform duration-300 md:static md:inset-auto md:translate-x-0 md:transition-all"
      :class="[
        uiStore.mobileSidebarOpen ? 'translate-x-0' : '-translate-x-[calc(100%+0.5rem)]',
        uiStore.sidebarCollapsed ? 'md:w-[76px]' : 'md:w-64',
      ]"
    >
      <div
        class="flex h-16 items-center gap-2 px-4"
        :class="uiStore.sidebarCollapsed ? 'justify-center' : 'justify-between'"
      >
        <router-link to="/app" class="flex min-w-0 items-center gap-2.5">
          <StarterLogo :show-text="!uiStore.sidebarCollapsed" />
        </router-link>
        <button
          v-if="!uiStore.sidebarCollapsed"
          class="gemini-icon-btn h-9 w-9 shrink-0"
          title="收起侧边栏"
          @click="uiStore.toggleSidebar()"
        >
          «
        </button>
      </div>

      <button
        v-if="uiStore.sidebarCollapsed"
        class="gemini-icon-btn mx-auto mb-2 h-9 w-9"
        title="展开侧边栏"
        @click="uiStore.toggleSidebar()"
      >
        »
      </button>

      <nav class="flex-1 overflow-y-auto px-3 py-2">
        <router-link
          to="/app"
          class="mb-1 flex items-center gap-3 rounded-pill px-3.5 py-2.5 text-sm font-medium transition-colors"
          :class="isActive('/app') ? 'bg-primary-soft text-primary' : 'text-content-secondary hover:bg-surface-hover hover:text-content'"
        >
          <span class="shrink-0 text-base">⬡</span>
          <span v-if="!uiStore.sidebarCollapsed">我的笔记本</span>
        </router-link>

        <div v-if="!uiStore.sidebarCollapsed" class="mt-5 px-2">
          <p class="mb-2 px-1.5 text-xs font-medium uppercase tracking-wide text-content-secondary">
            最近
          </p>
          <router-link
            v-for="nb in notebookStore.notebooks.slice(0, 8)"
            :key="nb.id"
            :to="`/app/notebook/${nb.id}`"
            class="mb-0.5 block truncate rounded-pill px-3 py-2 text-sm text-content-secondary transition-colors hover:bg-surface-hover hover:text-content"
          >
            {{ nb.name }}
          </router-link>
        </div>
      </nav>

      <div class="p-3">
        <div
          v-if="!uiStore.sidebarCollapsed && userStore.profile"
          class="mb-1 flex items-center gap-3 rounded-pill px-3 py-2 text-sm text-content"
        >
          <span class="flex h-8 w-8 shrink-0 items-center justify-center rounded-pill bg-primary-soft text-xs font-semibold uppercase text-primary">
            {{ userStore.profile.username.slice(0, 1) }}
          </span>
          <span class="truncate">{{ userStore.profile.username }}</span>
        </div>
        <button
          class="gemini-btn gemini-btn-ghost mb-0.5 w-full gap-3 px-3 py-2.5"
          :class="uiStore.sidebarCollapsed ? 'justify-center' : 'justify-start'"
          @click="uiStore.toggleDarkMode()"
        >
          <span class="shrink-0 text-base">{{ uiStore.darkMode ? '☀' : '☾' }}</span>
          <span v-if="!uiStore.sidebarCollapsed">{{ uiStore.darkMode ? '浅色模式' : '深色模式' }}</span>
        </button>
        <button
          class="gemini-btn gemini-btn-ghost w-full gap-3 px-3 py-2.5"
          :class="uiStore.sidebarCollapsed ? 'justify-center' : 'justify-start'"
          @click="handleLogout"
        >
          <span class="shrink-0 text-base">⏻</span>
          <span v-if="!uiStore.sidebarCollapsed">退出登录</span>
        </button>
      </div>
    </aside>

    <main class="relative flex flex-1 flex-col overflow-hidden rounded-2xl bg-surface-elevated shadow-gsm">
      <!-- 右上角若隐若现的绿色微光 -->
      <div class="pointer-events-none absolute right-0 top-0 h-80 w-80 -translate-y-1/3 translate-x-1/3 rounded-full bg-primary opacity-[0.07] blur-3xl" />
      <button
        class="gemini-icon-btn absolute left-3 top-3 z-10 h-9 w-9 md:hidden"
        title="打开菜单"
        @click="uiStore.toggleMobileSidebar()"
      >
        ☰
      </button>
      <router-view />
    </main>
  </div>
</template>

<script setup lang="ts">
import { onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import StarterLogo from '@/components/brand/StarterLogo.vue'
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

watch(() => route.fullPath, () => {
  uiStore.closeMobileSidebar()
})

async function handleLogout() {
  await userStore.logout()
  router.push('/login')
}

onMounted(() => {
  notebookStore.fetchNotebooks().catch(() => {})
})
</script>
