import { ref, type Ref } from 'vue'
import { chatApi, type Message, type SearchMode } from '@/api/chat'

type ScrollBehaviorOption = 'auto' | 'smooth'

interface UseChatStreamingOptions {
  activeConversationId: Ref<number | null>
  input: Ref<string>
  messages: Ref<Message[]>
  searchMode: Readonly<Ref<SearchMode>>
  loadMessages: () => Promise<void>
  scrollMessagesToBottom: (behavior?: ScrollBehaviorOption) => Promise<void>
}

export function useChatStreaming({
  activeConversationId,
  input,
  messages,
  searchMode,
  loadMessages,
  scrollMessagesToBottom,
}: UseChatStreamingOptions) {
  const sending = ref(false)
  const streamingAssistantId = ref<number | null>(null)
  const sendFailed = ref(false)

  function appendMessage(message: Message) {
    if (messages.value.some((item) => item.id === message.id)) return
    messages.value = [...messages.value, message]
  }

  function appendAssistantDelta(conversationId: number, delta: string) {
    if (!delta) return

    const existingId = streamingAssistantId.value
    if (!existingId) {
      const nextId = -Date.now()
      streamingAssistantId.value = nextId
      messages.value = [
        ...messages.value,
        {
          id: nextId,
          conversation_id: conversationId,
          role: 'assistant',
          content: '',
          citations: [],
          created_at: new Date().toISOString(),
        },
      ]
    }

    messages.value = messages.value.map((message) => {
      if (message.id !== streamingAssistantId.value) return message
      return {
        ...message,
        content: `${message.content}${delta}`,
      }
    })
  }

  function replaceStreamingAssistant(message: Message) {
    const existingId = streamingAssistantId.value
    if (!existingId) {
      appendMessage(message)
      return
    }

    messages.value = messages.value.map((item) => (
      item.id === existingId ? message : item
    ))
  }

  async function sendMessage() {
    if (!input.value.trim() || !activeConversationId.value) return
    const content = input.value.trim()
    const conversationId = activeConversationId.value
    input.value = ''
    sending.value = true
    streamingAssistantId.value = null
    sendFailed.value = false
    let receivedUserMessage = false
    await scrollMessagesToBottom('smooth')
    try {
      await chatApi.sendMessageStream(
        conversationId,
        content,
        searchMode.value,
        {
          onUserMessage: (message) => {
            receivedUserMessage = true
            appendMessage(message)
            void scrollMessagesToBottom('smooth')
          },
          onDelta: (delta) => {
            appendAssistantDelta(conversationId, delta)
            void scrollMessagesToBottom('smooth')
          },
          onAssistantMessage: (message) => {
            replaceStreamingAssistant(message)
            void scrollMessagesToBottom('smooth')
          },
        },
      )
    } catch {
      if (!receivedUserMessage) {
        await sendMessageWithoutStreaming(conversationId, content)
      } else {
        await loadMessages()
      }
    } finally {
      streamingAssistantId.value = null
      sending.value = false
    }
  }

  async function sendMessageWithoutStreaming(
    conversationId: number,
    content: string,
  ) {
    try {
      const { data } = await chatApi.sendMessage(
        conversationId,
        content,
        searchMode.value,
      )
      appendMessage(data.user_message)
      appendMessage(data.assistant_message)
      await scrollMessagesToBottom('smooth')
    } catch {
      input.value = content
      sendFailed.value = true
    }
  }

  return {
    sending,
    streamingAssistantId,
    sendFailed,
    sendMessage,
    appendMessage,
    appendAssistantDelta,
    replaceStreamingAssistant,
    sendMessageWithoutStreaming,
  }
}
