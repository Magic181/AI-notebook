<template>
  <div class="flex h-full">
    <aside class="hidden w-64 shrink-0 border-r border-line bg-surface-secondary md:block">
      <div class="px-4 py-4">
        <p class="text-sm font-medium text-content">会话</p>
        <p class="mt-1 text-xs text-content-secondary">{{ notebookDisplayLabel }}</p>
      </div>
      <div class="px-3 pb-2">
        <button
          class="gemini-btn gemini-btn-tonal w-full"
          :disabled="creatingConversation"
          @click="createConversation()"
        >
          <span class="text-base leading-none">+</span>
          {{ creatingConversation ? '创建中...' : '新会话' }}
        </button>
      </div>
      <div class="max-h-[calc(100vh-130px)] overflow-y-auto px-2 pb-2">
        <div
          v-if="initLoading"
          class="flex items-center justify-center py-6 text-sm text-content-secondary"
        >
          加载中...
        </div>
        <div
          v-if="initError"
          class="flex flex-col items-center gap-2 rounded-glg border border-dashed border-line px-3 py-6 text-center"
        >
          <p class="text-sm text-content-secondary">加载会话失败</p>
          <button class="gemini-btn gemini-btn-ghost gemini-btn-sm" @click="initChat">
            重试
          </button>
        </div>
        <div
          v-for="c in conversations"
          :key="c.id"
          class="group mb-1 flex min-h-[44px] items-center gap-1 rounded-pill px-1 transition-colors"
          :class="c.id === activeConversationId ? 'bg-primary-soft' : 'hover:bg-surface-hover'"
        >
          <form
            v-if="editingConversationId === c.id"
            class="flex min-w-0 flex-1 items-center gap-1"
            @submit.prevent="saveConversationTitle(c)"
          >
            <input
              v-model="editingConversationTitle"
              class="min-w-0 flex-1 rounded-pill border border-primary/30 bg-surface-elevated px-3 py-1.5 text-sm text-content outline-none focus:border-primary focus:ring-2 focus:ring-primary-soft"
              maxlength="100"
              autofocus
              @keydown.esc.prevent="cancelEditingConversation"
            />
            <button
              type="submit"
              class="gemini-btn gemini-btn-tonal gemini-btn-sm shrink-0"
              :disabled="renamingConversation"
            >
              保存
            </button>
          </form>
          <button
            v-else
            class="min-w-0 flex-1 truncate px-4 py-2 text-left text-sm"
            :class="c.id === activeConversationId ? 'font-medium text-primary' : 'text-content-secondary hover:text-content'"
            @click="selectConversation(c.id)"
          >
            {{ c.title || '未命名会话' }}
          </button>
          <button
            v-if="editingConversationId !== c.id"
            class="gemini-btn gemini-btn-ghost gemini-btn-sm shrink-0 opacity-0 group-hover:opacity-100"
            :disabled="renamingConversation"
            @click="startEditingConversation(c)"
          >
            编辑
          </button>
          <button
            v-if="editingConversationId !== c.id"
            class="gemini-btn gemini-btn-danger gemini-btn-sm mr-1 shrink-0 opacity-0 group-hover:opacity-100"
            :disabled="deletingConversation || renamingConversation"
            @click="openDeleteConversation(c)"
          >
            删除
          </button>
        </div>
      </div>
    </aside>

    <div class="flex flex-1 flex-col">
      <header class="flex h-16 shrink-0 items-center justify-between px-6">
        <div class="min-w-0">
          <h2 class="truncate text-lg font-semibold tracking-tight">
            <span class="gemini-gradient-text">AI 对话</span>
          </h2>
          <p class="truncate text-xs text-content-secondary">
            {{ headerHint }}
          </p>
        </div>
        <div class="flex shrink-0 items-center gap-2 md:hidden">
          <button
            class="gemini-btn gemini-btn-ghost"
            @click="createConversation()"
          >
            新会话
          </button>
          <button
            v-if="activeConversation"
            class="gemini-btn gemini-btn-danger"
            :disabled="deletingConversation"
            @click="openDeleteConversation(activeConversation)"
          >
            删除
          </button>
        </div>
      </header>

      <div class="flex min-h-0 flex-1">
        <div
          ref="messagesViewport"
          class="h-full min-w-0 flex-1 space-y-4 overflow-y-auto p-6"
          @scroll="handleMessagesScroll"
        >
          <MessageList
            :messages="messages"
            :loading="loadingMessages"
            :empty-state-hint="emptyStateHint"
            :sending="sending"
            :streaming-assistant-id="streamingAssistantId"
            :set-message-element="setMessageElement"
            @action="handleActionItem"
          />
        </div>

        <ConversationJumpNav
          class="hidden shrink-0 pr-1 xl:block"
          :items="messageJumpItems"
          :active-id="activeJumpMessageId"
          @jump="scrollToMessage"
        />
      </div>

      <ChatComposer
        v-model="input"
        v-model:web-search-enabled="webSearchEnabled"
        :sending="sending"
        :send-failed="sendFailed"
        :active-conversation-id="activeConversationId"
        @send="sendMessage"
      />
    </div>
  </div>

  <BaseModal
    :model-value="!!conversationToDelete"
    title="确认删除会话"
    max-width="sm"
    @update:model-value="(open) => { if (!open) conversationToDelete = null }"
  >
    <p class="mt-2 break-words text-sm text-content-secondary">
      确定要删除「{{ conversationToDelete?.title || '未命名会话' }}」吗？此操作会删除该会话下的所有消息。
    </p>
    <template #footer>
      <BaseButton variant="ghost" @click="conversationToDelete = null">
        取消
      </BaseButton>
      <BaseButton
        variant="danger"
        :disabled="deletingConversation"
        @click="deleteConversation"
      >
        {{ deletingConversation ? '删除中...' : '删除' }}
      </BaseButton>
    </template>
  </BaseModal>
</template>

<script setup lang="ts">
import { computed, nextTick, onBeforeUpdate, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { chatApi, type Conversation, type Message, type SearchMode } from '@/api/chat'
import ChatComposer from '@/components/chat/ChatComposer.vue'
import ConversationJumpNav from '@/components/chat/ConversationJumpNav.vue'
import MessageList from '@/components/chat/MessageList.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseModal from '@/components/ui/BaseModal.vue'
import { useChatStreaming } from '@/composables/useChatStreaming'
import { useNotebookStore } from '@/stores/notebook'

const route = useRoute()
const notebookStore = useNotebookStore()
const notebookId = computed(() => Number(route.params.id))

const conversations = ref<Conversation[]>([])
const activeConversationId = ref<number | null>(null)
const messages = ref<Message[]>([])
const input = ref('')
const webSearchEnabled = ref(false)
const messagesViewport = ref<HTMLElement | null>(null)
const conversationToDelete = ref<Conversation | null>(null)
const editingConversationId = ref<number | null>(null)
const editingConversationTitle = ref('')

const loadingMessages = ref(false)
const creatingConversation = ref(false)
const deletingConversation = ref(false)
const renamingConversation = ref(false)
const initLoading = ref(false)
const initError = ref(false)
const activeJumpMessageId = ref<number | null>(null)
const messageElements = new Map<number, HTMLElement>()
let jumpScrollFrame = 0

const searchMode = computed<SearchMode>(() => (webSearchEnabled.value ? 'hybrid' : 'local'))

const {
  sending,
  streamingAssistantId,
  sendFailed,
  sendMessage,
} = useChatStreaming({
  activeConversationId,
  input,
  messages,
  searchMode,
  loadMessages,
  scrollMessagesToBottom,
})

const headerHint = computed(() => {
  if (!activeConversationId.value) return '正在初始化会话...'
  return activeConversation.value?.title?.trim() || '新会话'
})

const activeConversation = computed(() => {
  return conversations.value.find((item) => item.id === activeConversationId.value) || null
})

const notebookDisplayLabel = computed(() => {
  const notebook = notebookStore.notebooks.find((item) => item.id === notebookId.value)
  if (notebook?.name?.trim()) return notebook.name
  if (notebookStore.currentNotebook?.id === notebookId.value && notebookStore.currentNotebook.name.trim()) {
    return notebookStore.currentNotebook.name
  }
  return '当前 Notebook'
})

const messageJumpItems = computed(() => {
  return messages.value
    .filter((message) => message.role === 'user')
    .map((message) => ({
      id: message.id,
      title: messageJumpTitle(message.content),
    }))
})

const emptyStateHint = computed(() => {
  if (webSearchEnabled.value) return '当前会同时结合 Notebook 文档和联网搜索结果回答。'
  return '当前会基于该 Notebook 的已解析文档进行检索并回答。'
})

onBeforeUpdate(() => {
  messageElements.clear()
})

async function scrollMessagesToBottom(behavior: 'auto' | 'smooth' = 'auto') {
  await nextTick()
  const el = messagesViewport.value
  if (!el) return
  el.scrollTo({
    top: el.scrollHeight,
    behavior,
  })
  updateActiveJumpMessage()
}

function setMessageElement(messageId: number, element: unknown) {
  if (element instanceof HTMLElement) {
    messageElements.set(messageId, element)
  }
}

function handleMessagesScroll() {
  if (jumpScrollFrame) return
  jumpScrollFrame = window.requestAnimationFrame(() => {
    jumpScrollFrame = 0
    updateActiveJumpMessage()
  })
}

function updateActiveJumpMessage() {
  const viewport = messagesViewport.value
  const items = messageJumpItems.value
  if (!viewport || !items.length) {
    activeJumpMessageId.value = null
    return
  }

  const viewportTop = viewport.getBoundingClientRect().top
  let activeId = items[0].id

  for (const item of items) {
    const element = messageElements.get(item.id)
    if (!element) continue
    const offset = element.getBoundingClientRect().top - viewportTop
    if (offset <= 96) {
      activeId = item.id
    } else {
      break
    }
  }

  activeJumpMessageId.value = activeId
}

async function scrollToMessage(messageId: number) {
  await nextTick()
  const element = messageElements.get(messageId)
  if (!element) return
  activeJumpMessageId.value = messageId
  element.scrollIntoView({
    behavior: 'smooth',
    block: 'start',
  })
}

function messageJumpTitle(content: string) {
  const title = content.replace(/\s+/g, ' ').trim()
  if (!title) return '新问题'
  return title.length > 16 ? `${title.slice(0, 16)}...` : title
}

function handleActionItem(action: string) {
  input.value = action
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

function startEditingConversation(conversation: Conversation) {
  editingConversationId.value = conversation.id
  editingConversationTitle.value = conversation.title || ''
}

function cancelEditingConversation() {
  editingConversationId.value = null
  editingConversationTitle.value = ''
}

async function saveConversationTitle(conversation: Conversation) {
  const title = editingConversationTitle.value.trim()
  renamingConversation.value = true
  try {
    const { data } = await chatApi.updateConversation(conversation.id, title)
    conversations.value = conversations.value.map((item) => (
      item.id === data.id ? data : item
    ))
    cancelEditingConversation()
  } catch {
    // error shown by axios interceptor
  } finally {
    renamingConversation.value = false
  }
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

watch(
  () => [messages.value.length, sending.value],
  () => {
    void scrollMessagesToBottom('smooth')
  },
  { flush: 'post' },
)

async function initChat() {
  initLoading.value = true
  initError.value = false
  try {
    if (!notebookStore.notebooks.length) {
      await notebookStore.fetchNotebooks().catch(() => {})
    }
    if (!notebookStore.notebooks.some((item) => item.id === notebookId.value)) {
      await notebookStore.fetchNotebook(notebookId.value).catch(() => {})
    }
    await loadConversations()
    if (!activeConversationId.value) {
      await createConversation()
    } else {
      await loadMessages()
    }
  } catch {
    initError.value = true
  } finally {
    initLoading.value = false
  }
}

onMounted(initChat)
</script>
