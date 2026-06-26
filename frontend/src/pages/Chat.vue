<template>
  <div class="flex h-full">
    <aside class="hidden w-64 shrink-0 border-r border-[var(--border)] bg-[var(--bg-secondary)] md:block">
      <div class="border-b border-[var(--border)] px-4 py-3">
        <p class="text-sm font-medium text-[var(--text)]">会话</p>
        <p class="mt-1 text-xs text-[var(--text-secondary)]">Notebook #{{ notebookId }}</p>
      </div>
      <div class="p-2">
        <button
          class="w-full rounded-lg bg-[var(--primary)] px-4 py-2 text-sm font-medium text-white hover:bg-[var(--primary-hover)]"
          :disabled="creatingConversation"
          @click="createConversation()"
        >
          {{ creatingConversation ? '创建中...' : '新会话' }}
        </button>
      </div>
      <div class="max-h-[calc(100vh-120px)] overflow-y-auto p-2">
        <div
          v-for="c in conversations"
          :key="c.id"
          class="mb-1 flex items-center gap-1 rounded-lg transition-colors"
          :class="c.id === activeConversationId ? 'bg-[var(--primary)]/10' : 'hover:bg-[var(--border)]'"
        >
          <button
            class="min-w-0 flex-1 truncate px-3 py-2 text-left text-sm"
            :class="c.id === activeConversationId ? 'text-[var(--primary)]' : 'text-[var(--text-secondary)] hover:text-[var(--text)]'"
            @click="selectConversation(c.id)"
          >
            {{ c.title || '未命名会话' }}
          </button>
          <button
            class="shrink-0 rounded-lg px-2 py-1.5 text-xs text-red-500 hover:bg-red-50 dark:hover:bg-red-950/30"
            :disabled="deletingConversation"
            @click="openDeleteConversation(c)"
          >
            删除
          </button>
        </div>
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
        <div class="flex shrink-0 items-center gap-2 md:hidden">
          <button
            class="rounded-lg px-3 py-2 text-sm text-[var(--text-secondary)] hover:bg-[var(--bg-secondary)]"
            @click="createConversation()"
          >
            新会话
          </button>
          <button
            v-if="activeConversation"
            class="rounded-lg px-3 py-2 text-sm text-red-500 hover:bg-red-50 dark:hover:bg-red-950/30"
            :disabled="deletingConversation"
            @click="openDeleteConversation(activeConversation)"
          >
            删除
          </button>
        </div>
      </header>

      <div ref="messagesViewport" class="flex-1 space-y-4 overflow-y-auto p-6">
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
          <div class="mb-4 h-10 w-10 rounded-lg border border-[var(--border)] bg-[var(--bg-secondary)]" />
          <p class="text-[var(--text)]">开始新的对话</p>
          <p class="mt-2 max-w-md text-sm text-[var(--text-secondary)]">
            {{ emptyStateHint }}
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
                class="whitespace-pre-wrap break-words rounded-lg px-4 py-3 text-sm leading-6"
                :class="
                  msg.role === 'user'
                    ? 'bg-[var(--primary)] text-white'
                    : 'bg-[var(--bg-secondary)] text-[var(--text)]'
                "
              >
                {{ msg.content }}
              </div>

              <CitationList
                v-if="msg.role === 'assistant'"
                :citations="msg.citations || []"
              />
            </div>
          </div>

          <div v-if="sending" class="text-sm text-[var(--text-secondary)]">正在生成回答...</div>
        </div>
      </div>

      <div class="shrink-0 border-t border-[var(--border)] p-4">
        <div class="mb-3 inline-flex rounded-lg border border-[var(--border)] bg-[var(--bg)] p-1 text-sm">
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
            class="flex-1 rounded-lg border border-[var(--border)] bg-[var(--bg)] px-4 py-3 text-[var(--text)] outline-none focus:border-[var(--primary)]"
          />
          <button
            type="submit"
            :disabled="!input.trim() || sending || !activeConversationId"
            class="rounded-lg bg-[var(--primary)] px-5 py-3 text-sm font-medium text-white hover:bg-[var(--primary-hover)] disabled:opacity-50"
          >
            发送
          </button>
        </form>
      </div>
    </div>
  </div>

  <div
    v-if="conversationToDelete"
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/40"
    @click.self="conversationToDelete = null"
  >
    <div class="w-full max-w-sm rounded-lg bg-[var(--bg)] p-6 shadow-xl">
      <h2 class="text-lg font-semibold text-[var(--text)]">确认删除会话</h2>
      <p class="mt-2 break-words text-sm text-[var(--text-secondary)]">
        确定要删除「{{ conversationToDelete.title || '未命名会话' }}」吗？此操作会删除该会话下的所有消息。
      </p>
      <div class="mt-6 flex justify-end gap-3">
        <button
          class="rounded-lg px-4 py-2 text-sm text-[var(--text-secondary)] hover:bg-[var(--bg-secondary)]"
          @click="conversationToDelete = null"
        >
          取消
        </button>
        <button
          :disabled="deletingConversation"
          class="rounded-lg bg-red-500 px-4 py-2 text-sm font-medium text-white hover:bg-red-600 disabled:opacity-50"
          @click="deleteConversation"
        >
          {{ deletingConversation ? '删除中...' : '删除' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { chatApi, type Conversation, type Message, type SearchMode } from '@/api/chat'
import CitationList from '@/components/chat/CitationList.vue'

const route = useRoute()
const notebookId = computed(() => Number(route.params.id))

const conversations = ref<Conversation[]>([])
const activeConversationId = ref<number | null>(null)
const messages = ref<Message[]>([])
const input = ref('')
const searchMode = ref<SearchMode>('local')
const messagesViewport = ref<HTMLElement | null>(null)
const conversationToDelete = ref<Conversation | null>(null)

const loadingMessages = ref(false)
const creatingConversation = ref(false)
const deletingConversation = ref(false)
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

const activeConversation = computed(() => {
  return conversations.value.find((item) => item.id === activeConversationId.value) || null
})

const emptyStateHint = computed(() => {
  if (searchMode.value === 'web') return '当前会优先使用联网搜索结果回答，适合查询最新资料。'
  if (searchMode.value === 'hybrid') return '当前会同时结合 Notebook 文档和联网搜索结果回答。'
  return '当前会基于该 Notebook 的已解析文档进行检索并回答。'
})

async function scrollMessagesToBottom() {
  await nextTick()
  const el = messagesViewport.value
  if (!el) return
  el.scrollTop = el.scrollHeight
}

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
  if (conversationId === activeConversationId.value) return
  activeConversationId.value = conversationId
  await loadMessages()
}

function openDeleteConversation(conversation: Conversation) {
  conversationToDelete.value = conversation
}

async function deleteConversation() {
  const conversation = conversationToDelete.value
  if (!conversation) return
  deletingConversation.value = true
  try {
    await chatApi.deleteConversation(conversation.id)
    conversations.value = conversations.value.filter((item) => item.id !== conversation.id)
    conversationToDelete.value = null

    if (activeConversationId.value !== conversation.id) return

    const nextConversation = conversations.value[0]
    if (nextConversation) {
      activeConversationId.value = nextConversation.id
      await loadMessages()
    } else {
      activeConversationId.value = null
      messages.value = []
      await createConversation()
    }
  } catch {
    // error shown by axios interceptor
  } finally {
    deletingConversation.value = false
  }
}

async function loadMessages() {
  if (!activeConversationId.value) return
  loadingMessages.value = true
  try {
    const { data } = await chatApi.listMessages(activeConversationId.value)
    messages.value = data
    await scrollMessagesToBottom()
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
    await scrollMessagesToBottom()
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
