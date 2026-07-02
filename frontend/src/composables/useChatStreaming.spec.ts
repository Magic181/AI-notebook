import { computed, ref } from 'vue'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { chatApi, type Message, type SearchMode } from '@/api/chat'
import { useChatStreaming } from './useChatStreaming'

vi.mock('@/api/chat', () => ({
  chatApi: {
    sendMessageStream: vi.fn(),
    sendMessage: vi.fn(),
  },
}))

function makeMessage(overrides: Partial<Message> = {}): Message {
  return {
    id: 1,
    conversation_id: 10,
    role: 'user',
    content: 'hello',
    citations: [],
    created_at: '2026-01-01T00:00:00Z',
    ...overrides,
  }
}

function makeHarness(searchModeValue: SearchMode = 'local') {
  const activeConversationId = ref<number | null>(10)
  const input = ref('Question')
  const messages = ref<Message[]>([])
  const searchMode = computed(() => searchModeValue)
  const loadMessages = vi.fn().mockResolvedValue(undefined)
  const scrollMessagesToBottom = vi.fn().mockResolvedValue(undefined)
  const streaming = useChatStreaming({
    activeConversationId,
    input,
    messages,
    searchMode,
    loadMessages,
    scrollMessagesToBottom,
  })

  return {
    activeConversationId,
    input,
    messages,
    searchMode,
    loadMessages,
    scrollMessagesToBottom,
    streaming,
  }
}

describe('useChatStreaming', () => {
  afterEach(() => {
    vi.restoreAllMocks()
    vi.clearAllMocks()
  })

  it('appends streamed user message, deltas and final assistant message', async () => {
    const userMessage = makeMessage({ id: 11, role: 'user', content: 'Question' })
    const assistantMessage = makeMessage({
      id: 12,
      role: 'assistant',
      content: 'Final answer',
    })
    vi.spyOn(Date, 'now').mockReturnValue(123)
    vi.mocked(chatApi.sendMessageStream).mockImplementation(async (_id, _content, _mode, handlers) => {
      handlers!.onUserMessage?.(userMessage)
      handlers!.onDelta?.('Partial')
      handlers!.onDelta?.(' answer')
      handlers!.onAssistantMessage?.(assistantMessage)
    })

    const harness = makeHarness('hybrid')
    await harness.streaming.sendMessage()

    expect(chatApi.sendMessageStream).toHaveBeenCalledWith(
      10,
      'Question',
      'hybrid',
      expect.any(Object),
    )
    expect(harness.input.value).toBe('')
    expect(harness.streaming.sending.value).toBe(false)
    expect(harness.streaming.streamingAssistantId.value).toBeNull()
    expect(harness.messages.value).toEqual([userMessage, assistantMessage])
    expect(harness.scrollMessagesToBottom).toHaveBeenCalledWith('smooth')
  })

  it('creates a temporary assistant message while deltas are streaming', () => {
    vi.spyOn(Date, 'now').mockReturnValue(456)
    const harness = makeHarness()

    harness.streaming.appendAssistantDelta(10, 'Hello')
    harness.streaming.appendAssistantDelta(10, ' there')

    expect(harness.streaming.streamingAssistantId.value).toBe(-456)
    expect(harness.messages.value).toHaveLength(1)
    expect(harness.messages.value[0]).toMatchObject({
      id: -456,
      conversation_id: 10,
      role: 'assistant',
      content: 'Hello there',
      citations: [],
    })
  })

  it('falls back to non-streaming send when stream fails before user message arrives', async () => {
    const userMessage = makeMessage({ id: 21, role: 'user', content: 'Question' })
    const assistantMessage = makeMessage({
      id: 22,
      role: 'assistant',
      content: 'Fallback answer',
    })
    vi.mocked(chatApi.sendMessageStream).mockRejectedValue(new Error('stream failed'))
    vi.mocked(chatApi.sendMessage).mockResolvedValue({
      data: {
        user_message: userMessage,
        assistant_message: assistantMessage,
      },
    } as never)

    const harness = makeHarness()
    await harness.streaming.sendMessage()

    expect(chatApi.sendMessage).toHaveBeenCalledWith(10, 'Question', 'local')
    expect(harness.messages.value).toEqual([userMessage, assistantMessage])
    expect(harness.input.value).toBe('')
    expect(harness.streaming.sendFailed.value).toBe(false)
    expect(harness.loadMessages).not.toHaveBeenCalled()
  })

  it('restores input when both stream and fallback send fail', async () => {
    vi.mocked(chatApi.sendMessageStream).mockRejectedValue(new Error('stream failed'))
    vi.mocked(chatApi.sendMessage).mockRejectedValue(new Error('send failed'))

    const harness = makeHarness()
    await harness.streaming.sendMessage()

    expect(harness.input.value).toBe('Question')
    expect(harness.messages.value).toEqual([])
    expect(harness.streaming.sendFailed.value).toBe(true)
  })

  it('reloads messages when stream fails after user message arrives', async () => {
    const userMessage = makeMessage({ id: 31, role: 'user', content: 'Question' })
    vi.mocked(chatApi.sendMessageStream).mockImplementation(async (_id, _content, _mode, handlers) => {
      handlers!.onUserMessage?.(userMessage)
      throw new Error('stream failed')
    })

    const harness = makeHarness()
    await harness.streaming.sendMessage()

    expect(harness.messages.value).toEqual([userMessage])
    expect(harness.loadMessages).toHaveBeenCalledOnce()
    expect(harness.streaming.sendFailed.value).toBe(false)
    expect(chatApi.sendMessage).not.toHaveBeenCalled()
  })

  it('does not send blank messages or messages without an active conversation', async () => {
    const harness = makeHarness()
    harness.input.value = '   '
    await harness.streaming.sendMessage()

    harness.input.value = 'Question'
    harness.activeConversationId.value = null
    await harness.streaming.sendMessage()

    expect(chatApi.sendMessageStream).not.toHaveBeenCalled()
  })
})
