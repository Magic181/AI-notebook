<template>
  <div class="flex h-screen min-w-0 overflow-hidden bg-surface">
    <div v-if="uiStore.mobileSidebarOpen" class="fixed inset-0 z-30 bg-black/55 backdrop-blur-sm md:hidden" @click="uiStore.closeMobileSidebar()" />
    <AppSidebar />
    <main class="relative min-w-0 flex-1 overflow-hidden bg-surface">
      <div class="absolute inset-x-0 top-0 z-20 flex h-12 items-center border-b border-line bg-surface/90 px-3 backdrop-blur md:hidden">
        <button class="icon-button" title="打开导航" @click="uiStore.toggleMobileSidebar()"><AppIcon name="menu" class="h-5 w-5" /></button>
        <span class="ml-2 font-mono text-[10px] uppercase tracking-[0.16em] text-content-secondary">MindBase workspace</span>
      </div>
      <div class="h-full min-w-0 overflow-hidden pt-12 md:pt-0"><RouterView /></div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { watch } from 'vue'
import { useRoute } from 'vue-router'
import AppSidebar from '@/components/navigation/AppSidebar.vue'
import AppIcon from '@/components/ui/AppIcon.vue'
import { useUIStore } from '@/stores/ui'

const route = useRoute()
const uiStore = useUIStore()

watch(
  () => route.fullPath,
  () => uiStore.closeMobileSidebar(),
)
</script>
