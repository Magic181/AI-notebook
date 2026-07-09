<template>
  <div class="inline-flex min-w-0 items-center gap-2.5">
    <span
      class="grid h-9 w-9 shrink-0 place-items-center rounded-control bg-primary text-sm font-bold text-white shadow-gsm"
      aria-hidden="true"
    >
      <svg viewBox="0 0 24 24" class="h-5 w-5" fill="none">
        <path
          d="M6.5 6.8c0-1.2 1-2.2 2.2-2.2h6.6c1.2 0 2.2 1 2.2 2.2v10.4c0 1.2-1 2.2-2.2 2.2H8.7c-1.2 0-2.2-1-2.2-2.2V6.8Z"
          stroke="currentColor"
          stroke-width="1.8"
        />
        <path
          d="M9.3 8.4h5.4M9.3 11.7h5.4M9.3 15h3.2"
          stroke="currentColor"
          stroke-linecap="round"
          stroke-width="1.8"
        />
      </svg>
    </span>
    <span v-if="showText" class="min-w-0">
      <span class="block truncate text-base font-semibold tracking-tight text-content">
        {{ title }}
      </span>
      <span v-if="subtitle" class="block truncate text-xs text-content-secondary">
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
  }>(),
  {
    title: 'AI Notebook Kit',
    subtitle: '',
    showText: true,
  },
)
</script>
