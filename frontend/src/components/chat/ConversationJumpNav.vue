<template>
  <div v-if="items.length > 1" class="jump-nav-host">
    <nav class="jump-rail" aria-label="会话位置导航">
      <button
        v-for="item in items"
        :key="item.id"
        type="button"
        class="jump-item"
        :class="{ 'jump-item-active': item.id === activeId }"
        @click="$emit('jump', item.id)"
      >
        <span class="jump-title">{{ item.title }}</span>
        <span class="jump-marker" />
      </button>
    </nav>

    <button
      type="button"
      class="jump-touch-trigger"
      aria-label="打开消息位置列表"
      @click="isSheetOpen = true"
    >
      <span class="jump-touch-dot" />
      <span class="jump-touch-dot" />
      <span class="jump-touch-dot" />
    </button>

    <Teleport to="body">
      <div
        v-if="isSheetOpen"
        class="jump-sheet-overlay"
        @click.self="isSheetOpen = false"
      >
        <div class="jump-sheet" role="dialog" aria-label="会话位置导航">
          <div class="jump-sheet-header">
            <p class="jump-sheet-title">跳转到消息</p>
            <button
              type="button"
              class="jump-sheet-close"
              aria-label="关闭"
              @click="isSheetOpen = false"
            >
              ×
            </button>
          </div>
          <div class="jump-sheet-list">
            <button
              v-for="item in items"
              :key="`sheet-${item.id}`"
              type="button"
              class="jump-sheet-item"
              :class="{ 'jump-sheet-item-active': item.id === activeId }"
              @click="handleSheetSelect(item.id)"
            >
              {{ item.title }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

defineProps<{
  items: Array<{ id: number; title: string }>
  activeId: number | null
}>()

const emit = defineEmits<{
  jump: [id: number]
}>()

const isSheetOpen = ref(false)

function handleSheetSelect(id: number) {
  emit('jump', id)
  isSheetOpen.value = false
}
</script>

<style scoped>
.jump-nav-host {
  position: relative;
  display: flex;
  height: 100%;
  width: 2rem;
  flex-direction: column;
  align-items: flex-end;
  justify-content: center;
}

.jump-rail {
  position: absolute;
  top: 50%;
  right: 0;
  z-index: 20;
  display: flex;
  width: 2rem;
  max-width: min(14rem, calc(100vw - 1.5rem));
  max-height: min(70%, 34rem);
  transform: translateY(-50%);
  flex-direction: column;
  align-items: flex-end;
  overflow-y: auto;
  border-radius: var(--radius-card);
  padding: 0.45rem 0.35rem;
  background: transparent;
  transition:
    width 160ms ease,
    background-color 160ms ease,
    box-shadow 160ms ease,
    border-color 160ms ease,
    padding 160ms ease;
}

.jump-rail:hover,
.jump-rail:focus-within {
  width: min(14rem, calc(100vw - 1.5rem));
  border: 1px solid var(--border);
  background: color-mix(in srgb, var(--bg-elevated) 92%, transparent);
  box-shadow: var(--shadow-hover);
  backdrop-filter: blur(14px);
}

.jump-item {
  display: flex;
  width: 100%;
  align-items: center;
  justify-content: flex-end;
  gap: 0.75rem;
  border-radius: var(--radius-control);
  padding: 0.42rem 0.2rem;
  color: var(--text-secondary);
  font-size: 0.875rem;
  line-height: 1.2;
  transition:
    color 140ms ease,
    background-color 140ms ease,
    padding 140ms ease;
}

.jump-rail:hover .jump-item,
.jump-rail:focus-within .jump-item {
  padding: 0.45rem 0.35rem 0.45rem 0.7rem;
}

.jump-item:hover {
  color: var(--text);
  background: var(--primary-soft);
}

.jump-item-active {
  color: var(--primary);
  font-weight: 600;
}

.jump-title {
  min-width: 0;
  flex: 1;
  overflow: hidden;
  text-align: right;
  text-overflow: ellipsis;
  white-space: nowrap;
  opacity: 0;
  transform: translateX(0.35rem);
  transition:
    opacity 140ms ease,
    transform 140ms ease;
}

.jump-rail:hover .jump-title,
.jump-rail:focus-within .jump-title {
  opacity: 1;
  transform: translateX(0);
}

.jump-marker {
  height: 0.2rem;
  width: 0.5rem;
  flex-shrink: 0;
  border-radius: 9999px;
  background: var(--border);
  transition:
    width 140ms ease,
    background-color 140ms ease;
}

.jump-item-active .jump-marker {
  width: 0.95rem;
  background: var(--primary);
}

.jump-touch-trigger {
  display: none;
}

/* 触屏设备：隐藏悬停展开的导航条，改为点击弹出底部列表 */
@media (pointer: coarse) {
  .jump-rail {
    display: none;
  }

  .jump-touch-trigger {
    display: flex;
    width: 2rem;
    height: 2.5rem;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 0.2rem;
    border-radius: var(--radius-control);
    background: var(--bg-elevated);
    box-shadow: var(--shadow-default);
  }

  .jump-touch-dot {
    height: 0.3rem;
    width: 0.3rem;
    border-radius: 9999px;
    background: var(--text-secondary);
  }
}

.jump-sheet-overlay {
  position: fixed;
  inset: 0;
  z-index: 50;
  display: flex;
  align-items: flex-end;
  justify-content: center;
  background: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(2px);
}

.jump-sheet {
  width: 100%;
  max-width: 28rem;
  max-height: 70vh;
  overflow: hidden;
  border-radius: var(--radius-card) var(--radius-card) 0 0;
  background: var(--bg-elevated);
  box-shadow: var(--shadow-hover);
  display: flex;
  flex-direction: column;
}

.jump-sheet-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.25rem 0.5rem;
}

.jump-sheet-title {
  font-size: 0.9375rem;
  font-weight: 600;
  color: var(--text);
}

.jump-sheet-close {
  display: inline-flex;
  height: 1.75rem;
  width: 1.75rem;
  align-items: center;
  justify-content: center;
  border-radius: 9999px;
  color: var(--text-secondary);
  font-size: 1.1rem;
  line-height: 1;
}

.jump-sheet-close:hover {
  background: var(--surface-hover);
  color: var(--text);
}

.jump-sheet-list {
  overflow-y: auto;
  padding: 0.25rem 0.75rem 1rem;
}

.jump-sheet-item {
  display: block;
  width: 100%;
  border-radius: var(--radius-control);
  padding: 0.65rem 0.75rem;
  text-align: left;
  color: var(--text);
  font-size: 0.9375rem;
}

.jump-sheet-item:hover {
  background: var(--surface-hover);
}

.jump-sheet-item-active {
  color: var(--primary);
  font-weight: 600;
  background: var(--primary-soft);
}

</style>
