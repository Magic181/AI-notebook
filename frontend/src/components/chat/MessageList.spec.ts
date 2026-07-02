import { mount } from '@vue/test-utils'
import { afterEach, describe, expect, it, vi } from 'vitest'
import type { Message } from '@/api/chat'
import MessageList from './MessageList.vue'

function makeMessage(overrides: Partial<Message> = {}): Message {
  return {
    id: 1,
    conversation_id: 10,
    role: 'assistant',
    content: '1. Follow up',
    citations: [],
    created_at: '2026-01-01T00:00:00Z',
    ...overrides,
  }
}

function mountList(overrides = {}) {
  return mount(MessageList, {
    props: {
      messages: [],
      loading: false,
      emptyStateHint: 'Empty hint',
      sending: false,
      streamingAssistantId: null,
      setMessageElement: vi.fn(),
      ...overrides,
    },
    global: {
      stubs: {
        CitationList: true,
      },
    },
  })
}

describe('MessageList', () => {
  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('renders loading and empty states', () => {
    expect(mountList({ loading: true }).text()).toContain('加载中')
    expect(mountList().text()).toContain('Empty hint')
  })

  it('emits action text when an assistant action item is clicked', async () => {
    const wrapper = mountList({
      messages: [makeMessage()],
    })

    await wrapper.find('.ai-action-item').trigger('click')

    expect(wrapper.emitted('action')?.[0]).toEqual(['Follow up'])
  })

  it('renders a pending assistant indicator when sending without a streaming message', () => {
    const wrapper = mountList({
      messages: [makeMessage({ role: 'user', content: 'Question' })],
      sending: true,
    })

    expect(wrapper.findAll('.animate-bounce')).toHaveLength(3)
  })

  it('copies assistant message content', async () => {
    const writeText = vi.fn().mockResolvedValue(undefined)
    Object.defineProperty(navigator, 'clipboard', {
      configurable: true,
      value: { writeText },
    })
    const wrapper = mountList({
      messages: [makeMessage({ content: '  Answer text  ' })],
    })

    await wrapper.find('[aria-label="复制回答"]').trigger('click')
    await wrapper.vm.$nextTick()

    expect(writeText).toHaveBeenCalledWith('Answer text')
    expect(wrapper.find('[aria-label="已复制回答"]').exists()).toBe(true)
  })

  it('copies user message content', async () => {
    const writeText = vi.fn().mockResolvedValue(undefined)
    Object.defineProperty(navigator, 'clipboard', {
      configurable: true,
      value: { writeText },
    })
    const wrapper = mountList({
      messages: [makeMessage({ role: 'user', content: '  Question text  ' })],
    })

    await wrapper.find('[aria-label="复制问题"]').trigger('click')
    await wrapper.vm.$nextTick()

    expect(writeText).toHaveBeenCalledWith('Question text')
    expect(wrapper.find('[aria-label="已复制问题"]').exists()).toBe(true)
  })

  it('edits user message content in place before emitting it', async () => {
    const wrapper = mountList({
      messages: [makeMessage({ role: 'user', content: '  Question text  ' })],
    })

    await wrapper.find('[aria-label="修改问题"]').trigger('click')
    const textarea = wrapper.find<HTMLTextAreaElement>('[aria-label="修改问题内容"]')

    expect(textarea.exists()).toBe(true)

    await textarea.setValue('  Revised question  ')
    await wrapper.find('form.user-edit-bubble').trigger('submit')

    expect(wrapper.emitted('edit')?.[0]).toEqual(['Revised question'])
    expect(wrapper.find('[aria-label="修改问题内容"]').exists()).toBe(false)
  })

  it('cancels user message editing in place', async () => {
    const wrapper = mountList({
      messages: [makeMessage({ role: 'user', content: 'Question text' })],
    })

    await wrapper.find('[aria-label="修改问题"]').trigger('click')
    await wrapper.find('[aria-label="取消修改"]').trigger('click')

    expect(wrapper.find('[aria-label="修改问题内容"]').exists()).toBe(false)
    expect(wrapper.emitted('edit')).toBeUndefined()
  })
})
