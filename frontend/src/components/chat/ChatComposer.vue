<template>
  <div class="shrink-0 px-4 pb-5 pt-2">
    <div class="chat-composer mx-auto w-full max-w-3xl">
      <div class="px-3 pt-3">
        <div class="composer-source-controls" aria-label="回答资料来源">
          <button
            type="button"
            class="composer-source-pill"
            :class="{ 'composer-source-pill-active': webSearchEnabled }"
            :aria-pressed="webSearchEnabled"
            :disabled="sending"
            @click="emit('update:webSearchEnabled', !webSearchEnabled)"
          >
            联网搜索
          </button>
        </div>
      </div>
      <form
        class="flex items-center gap-2 px-4 pt-2"
        @submit.prevent="emit('send')"
      >
        <input
          :value="modelValue"
          type="text"
          placeholder="输入你的问题..."
          class="min-h-10 flex-1 bg-transparent text-content outline-none placeholder:text-content-secondary"
          @input="emit('update:modelValue', ($event.target as HTMLInputElement).value)"
        />
        <button
          type="submit"
          :disabled="!modelValue.trim() || sending || !activeConversationId"
          class="gemini-icon-btn gemini-icon-btn-primary shrink-0"
          aria-label="发送"
        >
          <svg viewBox="0 0 24 24" class="h-5 w-5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="12" y1="19" x2="12" y2="5" />
            <polyline points="5 12 12 5 19 12" />
          </svg>
        </button>
      </form>
      <div
        v-if="sendFailed"
        class="flex items-center justify-between gap-3 px-4 pb-3 pt-1"
      >
        <p class="text-xs font-medium text-danger">发送失败</p>
        <button
          type="button"
          class="composer-retry-btn"
          :disabled="sending || !modelValue.trim() || !activeConversationId"
          @click="emit('send')"
        >
          重试
        </button>
      </div>
      <div v-else class="pb-3" />
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  modelValue: string
  webSearchEnabled: boolean
  sending: boolean
  sendFailed: boolean
  activeConversationId: number | null
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string]
  'update:webSearchEnabled': [value: boolean]
  send: []
}>()
</script>

<style scoped>
.chat-composer {
  border-radius: 1.75rem;
  border: 1px solid rgba(226, 237, 231, 0.86);
  background: rgba(255, 255, 255, 0.88);
  box-shadow:
    0 18px 48px -32px rgba(16, 185, 129, 0.48),
    0 8px 26px -24px rgba(0, 0, 0, 0.28);
  backdrop-filter: blur(16px);
  transition:
    border-color 180ms ease,
    box-shadow 180ms ease,
    background-color 180ms ease;
}

.chat-composer:focus-within {
  border-color: rgba(16, 185, 129, 0.42);
  background: rgba(255, 255, 255, 0.96);
  box-shadow:
    0 0 0 4px rgba(16, 185, 129, 0.08),
    0 22px 54px -34px rgba(16, 185, 129, 0.56),
    0 8px 26px -24px rgba(0, 0, 0, 0.32);
}

.composer-source-controls {
  display: inline-flex;
  align-items: center;
  border-radius: 9999px;
  background: rgba(239, 244, 241, 0.72);
  padding: 0.25rem;
}

.composer-source-pill {
  display: inline-flex;
  min-height: 2rem;
  align-items: center;
  justify-content: center;
  border-radius: 9999px;
  padding: 0.35rem 1rem;
  color: #66756f;
  font-size: 0.875rem;
  font-weight: 650;
  line-height: 1;
  transition:
    background-color 160ms ease,
    color 160ms ease,
    box-shadow 160ms ease,
    transform 160ms ease;
}

.composer-source-pill:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.66);
  color: #2f3f38;
}

.composer-source-pill:active:not(:disabled) {
  transform: translateY(1px);
}

.composer-source-pill:focus-visible {
  outline: 2px solid rgba(16, 185, 129, 0.28);
  outline-offset: 2px;
}

.composer-source-pill:disabled {
  cursor: not-allowed;
  opacity: 0.62;
}

.composer-source-pill-active {
  background: #e8f7f0;
  color: #047857;
  box-shadow: inset 0 0 0 1px rgba(16, 185, 129, 0.08);
}

.composer-retry-btn {
  display: inline-flex;
  min-height: 1.75rem;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-pill);
  padding: 0.25rem 0.7rem;
  color: #b3261e;
  font-size: 0.75rem;
  font-weight: 700;
  line-height: 1;
  transition:
    background-color 140ms ease,
    box-shadow 140ms ease;
}

.composer-retry-btn:hover:not(:disabled) {
  background: rgba(179, 38, 30, 0.08);
}

.composer-retry-btn:focus-visible {
  outline: none;
  box-shadow: 0 0 0 3px rgba(179, 38, 30, 0.14);
}

.composer-retry-btn:disabled {
  cursor: not-allowed;
  opacity: 0.48;
}

:global(.dark) .chat-composer {
  border-color: rgba(42, 53, 48, 0.86);
  background: rgba(30, 36, 33, 0.88);
}

:global(.dark) .chat-composer:focus-within {
  border-color: rgba(52, 211, 153, 0.36);
  background: rgba(30, 36, 33, 0.96);
}

:global(.dark) .composer-source-controls {
  background: rgba(18, 22, 20, 0.72);
}

:global(.dark) .composer-source-pill {
  color: #8ea099;
}

:global(.dark) .composer-source-pill:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.06);
  color: #d7e4df;
}

:global(.dark) .composer-source-pill-active {
  background: rgba(16, 185, 129, 0.16);
  color: #7dd3a8;
  box-shadow: inset 0 0 0 1px rgba(16, 185, 129, 0.16);
}
</style>
