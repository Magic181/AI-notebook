<template>
  <aside
    class="fixed inset-y-0 left-0 z-40 flex w-[min(88vw,17rem)] flex-col border-r border-white/[0.07] bg-ink text-white shadow-2xl transition-transform duration-300 md:static md:w-[264px] md:translate-x-0 md:shadow-none md:transition-[width]"
    :class="[
      uiStore.mobileSidebarOpen ? 'translate-x-0' : '-translate-x-full',
      uiStore.sidebarCollapsed ? 'md:w-[72px]' : 'md:w-[264px]',
    ]"
  >
    <div class="flex h-[72px] shrink-0 items-center border-b border-white/[0.07] px-4" :class="uiStore.sidebarCollapsed ? 'justify-center' : 'justify-between'">
      <RouterLink to="/app" class="min-w-0 overflow-hidden">
        <StarterLogo tone="inverse" :show-text="!uiStore.sidebarCollapsed" title="MindBase Kit" subtitle="starter workspace" />
      </RouterLink>
      <button v-if="!uiStore.sidebarCollapsed" class="icon-button h-9 w-9 text-white/45 hover:bg-white/10 hover:text-white" title="收起导航" @click="uiStore.toggleSidebar()">
        <AppIcon name="chevron-left" class="h-4 w-4" />
      </button>
    </div>

    <button v-if="uiStore.sidebarCollapsed" class="icon-button mx-auto mt-3 h-9 w-9 text-white/45 hover:bg-white/10 hover:text-white" title="展开导航" @click="uiStore.toggleSidebar()">
      <AppIcon name="chevron-right" class="h-4 w-4" />
    </button>

    <nav class="min-h-0 flex-1 overflow-y-auto px-3 py-5">
      <p v-if="!uiStore.sidebarCollapsed" class="mb-3 px-3 text-[10px] font-semibold uppercase tracking-[0.14em] text-white/30">Workspace</p>
      <RouterLink
        v-for="item in starterConfig.navigation"
        :key="item.to"
        :to="item.to"
        class="group mb-1 flex min-h-[42px] items-center gap-3 rounded-control border px-3 text-[13px] font-medium transition"
        :class="[
          isActive(item.match) ? 'border-white/10 bg-white/[0.09] text-white shadow-[inset_0_1px_0_rgba(255,255,255,0.04)]' : 'border-transparent text-white/48 hover:bg-white/[0.055] hover:text-white/85',
          uiStore.sidebarCollapsed ? 'justify-center' : '',
        ]"
      >
        <AppIcon :name="item.icon" class="h-[18px] w-[18px] shrink-0" />
        <span v-if="!uiStore.sidebarCollapsed" class="min-w-0 flex-1 truncate">{{ item.label }}</span>
        <span v-if="item.optional && !uiStore.sidebarCollapsed" class="rounded-md border border-white/10 bg-white/[0.035] px-1.5 py-0.5 text-[8px] uppercase tracking-[0.1em] text-white/35">optional</span>
      </RouterLink>

      <div v-if="!uiStore.sidebarCollapsed" class="mt-7 border-t border-white/[0.07] pt-5">
        <div class="mb-3 flex items-center justify-between px-3">
          <p class="text-[10px] font-semibold uppercase tracking-[0.14em] text-white/30">Recent spaces</p>
          <span class="text-[10px] text-white/25">{{ notebookStore.notebooks.length }}</span>
        </div>
        <RouterLink v-for="notebook in notebookStore.notebooks.slice(0, 6)" :key="notebook.id" :to="`/app/notebook/${notebook.id}`" class="mb-0.5 flex min-w-0 items-center gap-3 rounded-control px-3 py-2 text-[13px] text-white/40 transition hover:bg-white/[0.055] hover:text-white/80">
          <span class="h-1.5 w-1.5 shrink-0 rounded-full bg-primary" />
          <span class="truncate">{{ notebook.name }}</span>
        </RouterLink>
      </div>
    </nav>

    <div class="border-t border-white/[0.07] p-3">
      <div v-if="!uiStore.sidebarCollapsed && userStore.profile" class="mb-2 flex min-w-0 items-center gap-3 rounded-xl border border-white/[0.06] bg-white/[0.035] p-2.5">
        <span class="grid h-8 w-8 shrink-0 place-items-center rounded-lg bg-primary text-xs font-bold uppercase text-ink">{{ userStore.profile.username.slice(0, 1) }}</span>
        <div class="min-w-0">
          <p class="truncate text-[13px] font-medium text-white/90">{{ userStore.profile.username }}</p>
          <p class="mt-0.5 text-[9px] uppercase tracking-[0.1em] text-white/28">Local workspace</p>
        </div>
      </div>
      <div class="flex" :class="uiStore.sidebarCollapsed ? 'flex-col items-center' : 'gap-1'">
        <button class="icon-button text-white/45 hover:bg-white/10 hover:text-white" :class="uiStore.sidebarCollapsed ? '' : 'flex-1'" :title="uiStore.darkMode ? '切换浅色模式' : '切换深色模式'" @click="uiStore.toggleDarkMode()">
          <AppIcon :name="uiStore.darkMode ? 'sun' : 'moon'" class="h-[18px] w-[18px]" />
        </button>
        <button class="icon-button text-white/45 hover:bg-white/10 hover:text-white" :class="uiStore.sidebarCollapsed ? '' : 'flex-1'" title="退出登录" @click="handleLogout">
          <AppIcon name="logout" class="h-[18px] w-[18px]" />
        </button>
      </div>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import StarterLogo from '@/components/brand/StarterLogo.vue'
import AppIcon from '@/components/ui/AppIcon.vue'
import { starterConfig } from '@/config/starter'
import { useNotebookStore } from '@/stores/notebook'
import { useUIStore } from '@/stores/ui'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const notebookStore = useNotebookStore()
const uiStore = useUIStore()
const userStore = useUserStore()

function isActive(matchers: readonly string[]) {
  return matchers.some((path) => (path === '/app' ? route.path === path : route.path.startsWith(path)))
}

async function handleLogout() {
  await userStore.logout()
  await router.push('/login')
}

onMounted(() => {
  notebookStore.fetchNotebooks().catch(() => {})
})
</script>
