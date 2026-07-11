<template>
  <div class="shrink-0 border-t border-line/80 bg-surface-elevated/85 px-4 pb-4 pt-3 backdrop-blur-xl">
    <div class="chat-composer mx-auto w-full max-w-4xl">
      <div class="flex items-center justify-between border-b border-line/80 px-3.5 py-2">
        <button
          type="button"
          class="composer-source-pill source-toggle"
          :class="{ 'source-toggle-active': webSearchEnabled }"
          :aria-pressed="webSearchEnabled"
          :disabled="sending"
          @click="emit('update:webSearchEnabled', !webSearchEnabled)"
        >
          <span class="h-1.5 w-1.5 rounded-full" :class="webSearchEnabled ? 'bg-primary' : 'bg-content-secondary'" />
          {{ webSearchEnabled ? 'Hybrid · 本地 + 联网' : 'Local · 仅知识库' }}
        </button>
        <span class="text-[10px] font-medium text-content-secondary">Grounded answer</span>
      </div>
      <form class="flex items-center gap-3 px-4 py-3.5" @submit.prevent="emit('send')">
        <input
          :value="modelValue"
          type="text"
          placeholder="询问这个知识空间…"
          class="min-h-10 min-w-0 flex-1 bg-transparent text-[15px] text-content outline-none placeholder:text-content-secondary"
          @input="emit('update:modelValue', ($event.target as HTMLInputElement).value)"
        />
        <button v-if="canStopGeneration" type="button" class="icon-button icon-button-primary shrink-0" aria-label="停止生成" @click="emit('stop')">
          <svg viewBox="0 0 24 24" class="h-4 w-4" fill="currentColor" aria-hidden="true"><rect x="7" y="7" width="10" height="10" rx="1.5" /></svg>
        </button>
        <button v-else type="submit" :disabled="!modelValue.trim() || sending || !activeConversationId" class="icon-button icon-button-primary shrink-0" aria-label="发送">
          <svg viewBox="0 0 24 24" class="h-5 w-5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m5 12 7-7 7 7M12 5v14" /></svg>
        </button>
      </form>
      <div v-if="sendFailed" class="flex items-center justify-between gap-3 border-t border-line px-4 py-2">
        <p class="text-xs font-semibold text-red-600">发送失败</p>
        <button type="button" class="composer-retry-btn kit-button kit-button-danger kit-button-sm" :disabled="sending || !modelValue.trim() || !activeConversationId" @click="emit('send')">重试</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  modelValue: string
  webSearchEnabled: boolean
  sending: boolean
  sendFailed: boolean
  canStopGeneration: boolean
  activeConversationId: number | null
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string]
  'update:webSearchEnabled': [value: boolean]
  send: []
  stop: []
}>()
</script>

<style scoped>
.chat-composer {
  overflow: hidden;
  border: 1px solid var(--border);
  border-radius: 1.125rem;
  background: var(--bg-elevated);
  box-shadow: var(--shadow-sm);
  transition: border-color 150ms ease, box-shadow 150ms ease;
}

.chat-composer:focus-within {
  border-color: var(--primary);
  box-shadow: 0 0 0 4px var(--primary-soft), var(--shadow-sm);
}

.source-toggle {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  border-radius: var(--radius-control);
  padding: 0.35rem 0.5rem;
  color: var(--text-secondary);
  font-size: 0.68rem;
  font-weight: 600;
  transition: color 140ms ease, background-color 140ms ease;
}

.source-toggle:hover:not(:disabled),
.source-toggle-active {
  color: var(--text);
  background: var(--primary-soft);
}

.source-toggle:disabled {
  cursor: not-allowed;
  opacity: 0.5;
}
</style>
