<template>
  <div
    v-if="loading"
    class="flex h-full items-center justify-center text-sm text-content-secondary"
  >
    加载中...
  </div>

  <div
    v-else-if="messages.length === 0"
    class="flex h-full flex-col items-center justify-center text-center"
  >
    <div class="mb-5 flex h-12 w-12 items-center justify-center rounded-2xl bg-primary-soft text-primary">
      <svg viewBox="0 0 24 24" class="h-6 w-6" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
      </svg>
    </div>
    <p class="text-lg font-semibold text-content">开始新的对话</p>
    <p class="mt-2 max-w-md text-sm text-content-secondary">
      {{ emptyStateHint }}
    </p>
  </div>

  <div v-else class="space-y-5">
    <div
      v-for="msg in messages"
      :key="msg.id"
      :ref="(el) => setMessageElement(msg.id, el)"
      class="flex scroll-mt-6 gap-3"
      :class="msg.role === 'user' ? 'justify-end' : 'justify-start'"
    >
      <div
        v-if="msg.role === 'assistant'"
        class="ai-avatar mt-0.5"
      >
        <svg viewBox="0 0 24 24" class="h-4 w-4" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round">
          <path d="M12 3l1.35 4.15L17.5 8.5l-4.15 1.35L12 14l-1.35-4.15L6.5 8.5l4.15-1.35L12 3z" />
          <path d="M18 13l.75 2.25L21 16l-2.25.75L18 19l-.75-2.25L15 16l2.25-.75L18 13z" />
          <path d="M6 14l.55 1.45L8 16l-1.45.55L6 18l-.55-1.45L4 16l1.45-.55L6 14z" />
        </svg>
      </div>
      <div
        class="min-w-0"
        :class="msg.role === 'user' ? 'max-w-[80%]' : 'max-w-[min(880px,calc(100%-44px))]'"
      >
        <form
          v-if="msg.role === 'user' && editingMessageId === msg.id"
          class="user-edit-bubble rounded-2xl px-4 py-3 shadow-gsm"
          @submit.prevent="submitMessageEdit"
        >
          <textarea
            ref="editTextareaRef"
            v-model="editingContent"
            class="user-edit-textarea"
            rows="2"
            aria-label="修改问题内容"
            @keydown.esc.prevent="cancelMessageEdit"
            @keydown.enter.ctrl.prevent="submitMessageEdit"
            @keydown.enter.meta.prevent="submitMessageEdit"
          />
          <div class="mt-2 flex justify-end gap-1">
            <button
              type="button"
              class="user-edit-action-btn"
              aria-label="取消修改"
              title="取消修改"
              @click="cancelMessageEdit"
            >
              <svg viewBox="0 0 24 24" class="h-4 w-4" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                <path d="M18 6 6 18" />
                <path d="m6 6 12 12" />
              </svg>
            </button>
            <button
              type="submit"
              class="user-edit-action-btn user-edit-action-btn-primary"
              aria-label="提交修改"
              title="提交修改"
              :disabled="!editingContent.trim() || sending"
            >
              <svg viewBox="0 0 24 24" class="h-4 w-4" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                <path d="M20 6 9 17l-5-5" />
              </svg>
            </button>
          </div>
        </form>
        <div
          v-else-if="msg.role === 'user'"
          class="whitespace-pre-wrap break-words rounded-2xl bg-primary px-4 py-3 text-sm leading-7 text-primary-contrast shadow-gsm"
        >
          {{ msg.content }}
        </div>
        <div
          v-else
          class="assistant-message rounded-2xl bg-surface-elevated px-5 py-4 text-content shadow-gsm"
        >
          <div
            class="markdown-body"
            @click="handleActionItemClick"
            @keydown.enter="handleActionItemClick"
            @keydown.space.prevent="handleActionItemClick"
            v-html="markdownToHtml(msg.content)"
          />
        </div>

        <CitationList
          v-if="msg.role === 'assistant'"
          :citations="msg.citations || []"
        />
        <div
          v-if="editingMessageId !== msg.id"
          class="message-action-row"
          :class="msg.role === 'user' ? 'justify-end pr-1' : 'justify-start pl-1'"
        >
          <button
            type="button"
            class="message-action-btn"
            :aria-label="copyButtonLabel(msg)"
            :title="copyButtonLabel(msg)"
            @click="copyMessageContent(msg)"
          >
            <svg
              v-if="copiedMessageId === msg.id"
              viewBox="0 0 24 24"
              class="h-4 w-4"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
              aria-hidden="true"
            >
              <path d="M20 6 9 17l-5-5" />
            </svg>
            <svg
              v-else
              viewBox="0 0 24 24"
              class="h-4 w-4"
              fill="none"
              stroke="currentColor"
              stroke-width="1.9"
              stroke-linecap="round"
              stroke-linejoin="round"
              aria-hidden="true"
            >
              <rect x="9" y="9" width="11" height="11" rx="2" />
              <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
            </svg>
          </button>
          <button
            v-if="msg.role === 'user'"
            type="button"
            class="message-action-btn"
            aria-label="修改问题"
            title="修改问题"
            :disabled="sending"
            @click="startMessageEdit(msg)"
          >
            <svg viewBox="0 0 24 24" class="h-4 w-4" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
              <path d="M12 20h9" />
              <path d="M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4Z" />
            </svg>
          </button>
        </div>
      </div>
    </div>

    <div v-if="sending && !streamingAssistantId" class="flex items-center gap-3">
      <div class="ai-avatar">
        <svg viewBox="0 0 24 24" class="h-4 w-4" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round">
          <path d="M12 3l1.35 4.15L17.5 8.5l-4.15 1.35L12 14l-1.35-4.15L6.5 8.5l4.15-1.35L12 3z" />
          <path d="M18 13l.75 2.25L21 16l-2.25.75L18 19l-.75-2.25L15 16l2.25-.75L18 13z" />
        </svg>
      </div>
      <div class="flex gap-1.5 rounded-2xl bg-surface-elevated px-4 py-3.5 shadow-gsm">
        <span class="h-2 w-2 animate-bounce rounded-full bg-primary/60 [animation-delay:-0.3s]" />
        <span class="h-2 w-2 animate-bounce rounded-full bg-primary/60 [animation-delay:-0.15s]" />
        <span class="h-2 w-2 animate-bounce rounded-full bg-primary/60" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { nextTick, onBeforeUnmount, ref } from 'vue'
import type { Message } from '@/api/chat'
import CitationList from '@/components/chat/CitationList.vue'
import { markdownToHtml } from '@/utils/markdown'

const props = defineProps<{
  messages: Message[]
  loading: boolean
  emptyStateHint: string
  sending: boolean
  streamingAssistantId: number | null
  setMessageElement: (messageId: number, element: unknown) => void
}>()

const emit = defineEmits<{
  action: [value: string]
  edit: [value: string]
}>()

const copiedMessageId = ref<number | null>(null)
const editingMessageId = ref<number | null>(null)
const editingContent = ref('')
const editTextareaRef = ref<HTMLTextAreaElement | null>(null)
let copyResetTimer: ReturnType<typeof window.setTimeout> | null = null

onBeforeUnmount(() => {
  if (copyResetTimer) {
    window.clearTimeout(copyResetTimer)
  }
})

async function focusEditTextarea() {
  await nextTick()
  const textarea = Array.isArray(editTextareaRef.value)
    ? editTextareaRef.value[0]
    : editTextareaRef.value
  if (!(textarea instanceof HTMLTextAreaElement)) return
  textarea.focus()
  textarea.setSelectionRange(textarea.value.length, textarea.value.length)
}

function handleActionItemClick(event: Event) {
  const target = event.target as HTMLElement | null
  const item = target?.closest<HTMLElement>('.ai-action-item')
  if (!item) return
  const action = item.dataset.action
  if (!action) return
  emit('action', action)
}

function copyButtonLabel(message: Message) {
  if (copiedMessageId.value === message.id) {
    return message.role === 'user' ? '已复制问题' : '已复制回答'
  }
  return message.role === 'user' ? '复制问题' : '复制回答'
}

async function copyMessageContent(message: Message) {
  const content = message.content.trim()
  if (!content) return

  try {
    await copyText(content)
    copiedMessageId.value = message.id
    if (copyResetTimer) {
      window.clearTimeout(copyResetTimer)
    }
    copyResetTimer = window.setTimeout(() => {
      copiedMessageId.value = null
      copyResetTimer = null
    }, 1500)
  } catch {
    // Keep the interaction quiet; users can retry without losing context.
  }
}

function startMessageEdit(message: Message) {
  const content = message.content.trim()
  if (!content) return
  editingMessageId.value = message.id
  editingContent.value = content
  void focusEditTextarea()
}

function cancelMessageEdit() {
  editingMessageId.value = null
  editingContent.value = ''
}

function submitMessageEdit() {
  const content = editingContent.value.trim()
  if (!content || !editingMessageId.value || props.sending) return
  cancelMessageEdit()
  emit('edit', content)
}

async function copyText(content: string) {
  if (navigator.clipboard?.writeText) {
    await navigator.clipboard.writeText(content)
    return
  }

  const textarea = document.createElement('textarea')
  textarea.value = content
  textarea.setAttribute('readonly', '')
  textarea.style.position = 'fixed'
  textarea.style.opacity = '0'
  document.body.appendChild(textarea)
  textarea.select()
  document.execCommand('copy')
  document.body.removeChild(textarea)
}
</script>

<style scoped>
.assistant-message {
  overflow-wrap: anywhere;
  border-left: 2px solid var(--ai-accent-soft);
  box-shadow:
    inset 0 0 0 1px rgba(226, 237, 231, 0.54),
    0 12px 30px -26px rgba(16, 185, 129, 0.35);
}

.ai-avatar {
  display: flex;
  height: 2rem;
  width: 2rem;
  flex-shrink: 0;
  align-items: center;
  justify-content: center;
  border-radius: 9999px;
  color: var(--ai-accent);
  background: var(--ai-accent-soft);
  box-shadow: inset 0 0 0 1px rgba(124, 111, 240, 0.16);
}

.user-edit-bubble {
  border: 1px solid rgba(16, 185, 129, 0.32);
  background: var(--bg-elevated);
  box-shadow:
    0 0 0 3px rgba(16, 185, 129, 0.08),
    0 14px 32px -24px rgba(0, 0, 0, 0.26);
}

.user-edit-textarea {
  display: block;
  width: min(34rem, 72vw);
  min-width: min(18rem, 72vw);
  min-height: 5.5rem;
  resize: vertical;
  border: 0;
  background: transparent;
  color: var(--text);
  font-size: 0.875rem;
  line-height: 1.75;
  outline: none;
}

.user-edit-action-btn {
  display: inline-flex;
  height: 1.75rem;
  width: 1.75rem;
  align-items: center;
  justify-content: center;
  border-radius: 9999px;
  color: var(--text-secondary);
  transition:
    background-color 140ms ease,
    color 140ms ease,
    box-shadow 140ms ease,
    opacity 140ms ease,
    transform 140ms ease;
}

.user-edit-action-btn:hover:not(:disabled) {
  color: var(--text);
  background: var(--bg-secondary);
}

.user-edit-action-btn:active:not(:disabled) {
  transform: translateY(1px);
}

.user-edit-action-btn:focus-visible {
  outline: none;
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.16);
}

.user-edit-action-btn:disabled {
  cursor: not-allowed;
  opacity: 0.45;
}

.user-edit-action-btn-primary {
  color: var(--primary);
  background: var(--primary-soft);
}

.message-action-row {
  display: flex;
  align-items: center;
  gap: 0.2rem;
  min-height: 1.75rem;
  margin-top: 0.35rem;
}

.message-action-btn {
  display: inline-flex;
  height: 1.75rem;
  width: 1.75rem;
  align-items: center;
  justify-content: center;
  border-radius: 9999px;
  color: var(--text-secondary);
  opacity: 0.82;
  transition:
    background-color 140ms ease,
    color 140ms ease,
    box-shadow 140ms ease,
    opacity 140ms ease,
    transform 140ms ease;
}

.message-action-btn:hover {
  color: var(--text);
  background: var(--bg-secondary);
  opacity: 1;
}

.message-action-btn:active {
  transform: translateY(1px);
}

.message-action-btn:focus-visible {
  outline: none;
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.16);
}

:global(.dark) .markdown-body :deep(.table-scroll),
:global(.dark) .markdown-body :deep(table) {
  background: var(--bg-elevated);
}

:global(.dark) .markdown-body :deep(th) {
  background: var(--bg-secondary);
}

.markdown-body {
  font-size: 0.9375rem;
  line-height: 1.85;
}

.markdown-body :deep(p) {
  margin: 0 0 0.9rem;
}

.markdown-body :deep(p:last-child),
.markdown-body :deep(ul:last-child),
.markdown-body :deep(ol:last-child),
.markdown-body :deep(pre:last-child),
.markdown-body :deep(blockquote:last-child) {
  margin-bottom: 0;
}

.markdown-body :deep(h2),
.markdown-body :deep(h3),
.markdown-body :deep(h4),
.markdown-body :deep(h5) {
  margin: 1.1rem 0 0.45rem;
  color: var(--text);
  font-weight: 700;
  line-height: 1.4;
}

.markdown-body :deep(h2) {
  font-size: 1.125rem;
}

.markdown-body :deep(h3),
.markdown-body :deep(h4),
.markdown-body :deep(h5) {
  font-size: 1rem;
}

.markdown-body :deep(.ai-outline-block) {
  margin: 0.7rem 0 1rem;
  border: 1px solid var(--border);
  border-radius: var(--radius-card);
  background: var(--bg-secondary);
  padding: 0.15rem 0.9rem 0.6rem;
}

.markdown-body :deep(.ai-outline-summary) {
  cursor: pointer;
  padding: 0.6rem 0;
  color: var(--text-secondary);
  font-size: 0.8125rem;
  font-weight: 600;
  list-style: none;
}

.markdown-body :deep(.ai-outline-summary::-webkit-details-marker) {
  display: none;
}

.markdown-body :deep(.ai-outline-list) {
  margin: 0.2rem 0 0;
  padding: 0;
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 0.55rem;
}

.markdown-body :deep(.ai-outline-item) {
  position: relative;
  margin: 0;
  padding-left: 1.35rem;
  line-height: 1.6;
}

.markdown-body :deep(.ai-outline-item::before) {
  content: '';
  position: absolute;
  left: 0.15rem;
  top: 0.55rem;
  height: 0.375rem;
  width: 0.375rem;
  border-radius: 9999px;
  background: var(--text-secondary);
}

.markdown-body :deep(.ai-outline-sublist) {
  margin: 0.35rem 0 0;
  padding-left: 1.1rem;
  list-style: disc;
  color: var(--text-secondary);
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.markdown-body :deep(ul),
.markdown-body :deep(ol) {
  margin: 0.35rem 0 1rem 1.35rem;
  padding: 0;
}

.markdown-body :deep(ul) {
  list-style: disc;
}

.markdown-body :deep(ol) {
  list-style: decimal;
}

.markdown-body :deep(ol.ai-action-list) {
  margin: 0.5rem 0 1rem;
  padding: 0;
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.markdown-body :deep(.ai-action-item) {
  display: flex;
  align-items: flex-start;
  gap: 0.6rem;
  border-radius: var(--radius-card);
  background: var(--ai-accent-soft);
  box-shadow: var(--shadow-default);
  padding: 0.6rem 0.85rem;
  margin: 0;
  cursor: pointer;
  transition:
    box-shadow 140ms ease,
    background-color 140ms ease,
    transform 140ms ease;
}

.markdown-body :deep(.ai-action-item:hover) {
  background: var(--primary-soft);
  box-shadow: var(--shadow-hover);
}

.markdown-body :deep(.ai-action-item:active) {
  box-shadow: var(--shadow-active);
  transform: translateY(1px);
}

.markdown-body :deep(.ai-action-index) {
  display: inline-flex;
  height: 1.25rem;
  width: 1.25rem;
  flex-shrink: 0;
  align-items: center;
  justify-content: center;
  border-radius: 9999px;
  background: var(--ai-accent);
  color: #ffffff;
  font-size: 0.7rem;
  font-weight: 700;
  line-height: 1;
  margin-top: 0.1rem;
}

.markdown-body :deep(.ai-action-text) {
  min-width: 0;
  flex: 1;
  line-height: 1.6;
}

.markdown-body :deep(li) {
  margin: 0.25rem 0;
  padding-left: 0.2rem;
}

.markdown-body :deep(strong) {
  color: var(--text);
  font-weight: 700;
}

.markdown-body :deep(code) {
  border-radius: 0.35rem;
  background: var(--bg-secondary);
  padding: 0.1rem 0.35rem;
  color: var(--text);
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', monospace;
  font-size: 0.88em;
}

.markdown-body :deep(pre) {
  margin: 0.7rem 0 1rem;
  overflow-x: auto;
  border: 1px solid var(--border);
  border-radius: 0.75rem;
  background: var(--bg-secondary);
  padding: 0.9rem 1rem;
}

.markdown-body :deep(pre code) {
  display: block;
  background: transparent;
  padding: 0;
  white-space: pre;
}

.markdown-body :deep(blockquote) {
  margin: 0.7rem 0 1rem;
  border-left: 3px solid var(--primary);
  padding: 0.15rem 0 0.15rem 0.85rem;
  color: var(--text-secondary);
}

.markdown-body :deep(hr) {
  margin: 1.1rem 0;
  border: 0;
  border-top: 1px solid var(--border);
}

.markdown-body :deep(.table-scroll) {
  margin: 0.8rem 0 1.1rem;
  max-width: 100%;
  overflow-x: auto;
  border: 1px solid rgba(226, 237, 231, 0.72);
  border-radius: 0.75rem;
  background: #ffffff;
}

.markdown-body :deep(table) {
  width: 100%;
  min-width: 560px;
  border-collapse: collapse;
  background: #ffffff;
  font-size: 0.9rem;
  line-height: 1.65;
}

.markdown-body :deep(th),
.markdown-body :deep(td) {
  border-bottom: 1px solid rgba(226, 237, 231, 0.68);
  padding: 0.65rem 0.8rem;
  text-align: left;
  vertical-align: top;
}

.markdown-body :deep(th) {
  background: #f4f8f6;
  color: var(--text);
  font-weight: 700;
  white-space: nowrap;
}

.markdown-body :deep(tr:last-child td) {
  border-bottom: 0;
}

.markdown-body :deep(a) {
  color: var(--primary);
  text-decoration: underline;
  text-underline-offset: 0.18em;
}
</style>
