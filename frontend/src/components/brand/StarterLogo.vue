<template>
  <div class="inline-flex min-w-0 max-w-full items-center gap-2.5 overflow-hidden">
    <span
      class="relative grid h-9 w-9 shrink-0 place-items-center overflow-hidden rounded-xl border text-sm font-bold shadow-gsm"
      :class="tone === 'inverse' ? 'border-white/10 bg-primary text-ink' : 'border-ink/10 bg-ink text-white'"
      aria-hidden="true"
    >
      <span class="absolute left-1.5 top-1.5 h-2 w-2 border-l border-t border-current" />
      <span class="text-[10px] font-extrabold tracking-[-0.08em]">MB</span>
      <span class="absolute bottom-1.5 right-1.5 h-2 w-2 border-b border-r border-current" />
    </span>
    <span v-if="showText" class="min-w-0 overflow-hidden">
      <span
        class="block truncate text-[15px] font-[700] tracking-[-0.035em]"
        :class="tone === 'inverse' ? 'text-white' : 'text-content'"
      >
        {{ title }}<span class="text-primary">.</span>
      </span>
      <span v-if="subtitle" class="mt-0.5 block truncate text-[9px] font-medium uppercase tracking-[0.11em]" :class="tone === 'inverse' ? 'text-white/40' : 'text-content-secondary'">
        {{ subtitle }}
      </span>
    </span>
  </div>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    title?: string
    subtitle?: string
    showText?: boolean
    tone?: 'default' | 'inverse'
  }>(),
  {
    title: 'MindBase Kit',
    subtitle: '',
    showText: true,
    tone: 'default',
  },
)
</script>
