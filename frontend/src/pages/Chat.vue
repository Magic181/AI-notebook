<template>
  <div class="flex h-full">
    <aside class="hidden w-64 shrink-0 border-r border-[var(--border)] bg-[var(--bg-secondary)] md:block">
      <div class="border-b border-[var(--border)] px-4 py-3">
        <p class="text-sm font-medium text-[var(--text)]">会话</p>
        <p class="mt-1 text-xs text-[var(--text-secondary)]">Notebook #{{ notebookId }}</p>
      </div>
      <div class="p-2">
        <button
          class="w-full rounded-xl bg-[var(--primary)] px-4 py-2 text-sm font-medium text-white hover:bg-[var(--primary-hover)]"
          :disabled="creatingConversation"
          @click="createConversation()"
        >
          {{ creatingConversation ? '创建中...' : '+ 新会话' }}
        </button>
      </div>
      <div class="max-h-[calc(100vh-120px)] overflow-y-auto p-2">
        <button
          v-for="c in conversations"
          :key="c.id"
          class="mb-1 w-full truncate rounded-xl px-3 py-2 text-left text-sm transition-colors"
          :class="
            c.id === activeConversationId
              ? 'bg-[var(--primary)]/10 text-[var(--primary)]'
              : 'text-[var(--text-secondary)] hover:bg-[var(--border)] hover:text-[var(--text)]'
          "
          @click="selectConversation(c.id)"
        >
          {{ c.title || '未命名会话' }}
        </button>
      </div>
    </aside>

    <div class="flex flex-1 flex-col">
      <header class="flex h-14 shrink-0 items-center justify-between border-b border-[var(--border)] px-6">
        <div class="min-w-0">
          <h2 class="truncate font-medium text-[var(--text)]">AI 对话</h2>
          <p class="truncate text-xs text-[var(--text-secondary)]">
            {{ headerHint }}
          </p>
        </div>
        <button
          class="rounded-xl px-3 py-2 text-sm text-[var(--text-secondary)] hover:bg-[var(--bg-secondary)] md:hidden"
          @click="createConversation()"
        >
          新会话
        </button>
      </header>

      <div class="flex-1 space-y-4 overflow-y-auto p-6">
        <div
          v-if="loadingMessages"
          class="flex h-full items-center justify-center text-sm text-[var(--text-secondary)]"
        >
          加载中...
        </div>

        <div
          v-else-if="messages.length === 0"
          class="flex h-full flex-col items-center justify-center text-center"
        >
          <p class="text-4xl">💬</p>
          <p class="mt-4 text-[var(--text)]">开始与你的资料对话</p>
          <p class="mt-2 text-sm text-[var(--text-secondary)]">
            将基于该 Notebook 的文档进行检索并回答
          </p>
        </div>

        <div v-else class="space-y-4">
          <div
            v-for="msg in messages"
            :key="msg.id"
            class="flex"
            :class="msg.role === 'user' ? 'justify-end' : 'justify-start'"
          >
            <div class="max-w-[80%]">
              <div
                class="rounded-2xl px-4 py-3 text-sm"
                :class="
                  msg.role === 'user'
                    ? 'bg-[var(--primary)] text-white'
                    : 'bg-[var(--bg-secondary)] text-[var(--text)]'
                "
              >
                {{ msg.content }}
              </div>

              <div
                v-if="msg.role === 'assistant' && msg.citations?.length"
                class="mt-2 space-y-2"
              >
                <p class="text-xs text-[var(--text-secondary)]">引用来源</p>
                <div
                  v-for="(c, idx) in msg.citations"
                  :key="`${msg.id}-${idx}`"
                  class="rounded-xl border border-[var(--border)] bg-[var(--bg)] p-3 text-xs text-[var(--text-secondary)]"
                >
                  <template v-if="c.source_type === 'web'">
                    <a
                      :href="c.url"
                      target="_blank"
                      rel="noreferrer"
                      class="font-medium text-[var(--primary)] hover:underline"
                    >
                      {{ c.title }} · 网页 #{{ c.position }}
                    </a>
                    <p class="mt-1 line-clamp-3">{{ c.content }}</p>
                  </template>
                  <template v-else>
                    <p class="font-medium text-[var(--text)]">
                      {{ c.document_name }} · chunk #{{ c.position }}
                    </p>
                    <p class="mt-1 line-clamp-3">{{ c.chunk_text }}</p>
                  </template>
                </div>
              </div>
            </div>
          </div>

          <div v-if="sending" class="text-sm text-[var(--text-secondary)]">正在生成回答...</div>
        </div>
      </div>

      <div class="shrink-0 border-t border-[var(--border)] p-4">
        <div class="mb-3 inline-flex rounded-xl border border-[var(--border)] bg-[var(--bg)] p-1 text-sm">
          <button
            v-for="mode in searchModes"
            :key="mode.value"
            type="button"
            class="rounded-lg px-3 py-1.5 transition-colors"
            :class="
              searchMode === mode.value
                ? 'bg-[var(--primary)] text-white'
                : 'text-[var(--text-secondary)] hover:bg-[var(--bg-secondary)]'
            "
            :disabled="sending"
            @click="searchMode = mode.value"
          >
            {{ mode.label }}
          </button>
        </div>
        <form class="flex gap-3" @submit.prevent="sendMessage">
          <input
            v-model="input"
            type="text"
            placeholder="输入你的问题..."
            class="flex-1 rounded-xl border border-[var(--border)] bg-[var(--bg)] px-4 py-3 text-[var(--text)] outline-none focus:border-[var(--primary)]"
          />
          <button
            type="submit"
            :disabled="!input.trim() || sending || !activeConversationId"
            class="rounded-xl bg-[var(--primary)] px-5 py-3 text-sm font-medium text-white hover:bg-[var(--primary-hover)] disabled:opacity-50"
          >
            发送
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { chatApi, type Conversation, type Message, type SearchMode } from '@/api/chat'

const route = useRoute()
const notebookId = computed(() => Number(route.params.id))

const conversations = ref<Conversation[]>([])
const activeConversationId = ref<number | null>(null)
const messages = ref<Message[]>([])
const input = ref('')
const searchMode = ref<SearchMode>('local')

const loadingMessages = ref(false)
const creatingConversation = ref(false)
const sending = ref(false)

const searchModes: Array<{ label: string; value: SearchMode }> = [
  { label: '本地资料', value: 'local' },
  { label: '联网搜索', value: 'web' },
  { label: '混合', value: 'hybrid' },
]

const headerHint = computed(() => {
  if (!activeConversationId.value) return '正在初始化会话...'
  return `会话 #${activeConversationId.value}`
})

async function loadConversations() {
  const id = notebookId.value
  if (!id) return
  const { data } = await chatApi.listConversations(id)
  conversations.value = data
  if (!activeConversationId.value && data.length > 0) {
    activeConversationId.value = data[0].id
  }
}

async function createConversation() {
  const id = notebookId.value
  if (!id) return
  creatingConversation.value = true
  try {
    const { data } = await chatApi.createConversation(id, '')
    conversations.value = [data, ...conversations.value]
    activeConversationId.value = data.id
    await loadMessages()
  } catch {
    // error shown by axios interceptor
  } finally {
    creatingConversation.value = false
  }
}

async function selectConversation(conversationId: number) {
  activeConversationId.value = conversationId
  await loadMessages()
}

async function loadMessages() {
  if (!activeConversationId.value) return
  loadingMessages.value = true
  try {
    const { data } = await chatApi.listMessages(activeConversationId.value)
    messages.value = data
  } finally {
    loadingMessages.value = false
  }
}

async function sendMessage() {
  if (!input.value.trim() || !activeConversationId.value) return
  const content = input.value.trim()
  input.value = ''
  sending.value = true
  try {
    const { data } = await chatApi.sendMessage(
      activeConversationId.value,
      content,
      searchMode.value,
    )
    messages.value = [...messages.value, data.user_message, data.assistant_message]
  } catch {
    input.value = content
  } finally {
    sending.value = false
  }
}

onMounted(async () => {
  await loadConversations()
  if (!activeConversationId.value) {
    await createConversation()
  } else {
    await loadMessages()
  }
})
</script>
