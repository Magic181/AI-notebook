<template>
  <div class="flex h-full flex-col">
    <header class="flex h-14 shrink-0 items-center border-b border-[var(--border)] px-6">
      <h2 class="font-medium text-[var(--text)]">AI 对话</h2>
    </header>

    <div class="flex-1 space-y-4 overflow-y-auto p-6">
      <div
        v-if="chatStore.messages.length === 0"
        class="flex h-full flex-col items-center justify-center text-center"
      >
        <p class="text-4xl">💬</p>
        <p class="mt-4 text-[var(--text)]">开始与你的资料对话</p>
        <p class="mt-2 text-sm text-[var(--text-secondary)]">
          基于笔记本中的文档进行智能问答
        </p>
      </div>

      <div
        v-for="msg in chatStore.messages"
        :key="msg.id"
        class="flex"
        :class="msg.role === 'user' ? 'justify-end' : 'justify-start'"
      >
        <div
          class="max-w-[70%] rounded-2xl px-4 py-3 text-sm"
          :class="
            msg.role === 'user'
              ? 'bg-[var(--primary)] text-white'
              : 'bg-[var(--bg-secondary)] text-[var(--text)]'
          "
        >
          {{ msg.content }}
        </div>
      </div>
    </div>

    <div class="shrink-0 border-t border-[var(--border)] p-4">
      <form class="flex gap-3" @submit.prevent="sendMessage">
        <input
          v-model="input"
          type="text"
          placeholder="输入你的问题..."
          class="flex-1 rounded-xl border border-[var(--border)] bg-[var(--bg)] px-4 py-3 text-[var(--text)] outline-none focus:border-[var(--primary)]"
        />
        <button
          type="submit"
          :disabled="!input.trim()"
          class="rounded-xl bg-[var(--primary)] px-5 py-3 text-sm font-medium text-white hover:bg-[var(--primary-hover)] disabled:opacity-50"
        >
          发送
        </button>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useChatStore } from '@/stores/chat'

const chatStore = useChatStore()
const input = ref('')

function sendMessage() {
  if (!input.value.trim()) return
  chatStore.addMessage({
    id: Date.now().toString(),
    role: 'user',
    content: input.value,
    created_at: new Date().toISOString(),
  })
  input.value = ''
}
</script>
