<template>
  <svg
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    stroke-width="1.8"
    stroke-linecap="round"
    stroke-linejoin="round"
    aria-hidden="true"
  >
    <template v-if="name === 'grid'">
      <rect x="3.5" y="3.5" width="7" height="7" rx="1" />
      <rect x="13.5" y="3.5" width="7" height="7" rx="1" />
      <rect x="3.5" y="13.5" width="7" height="7" rx="1" />
      <rect x="13.5" y="13.5" width="7" height="7" rx="1" />
    </template>
    <template v-else-if="name === 'library'">
      <path d="M4 5.5h4v13H4zM10 5.5h4v13h-4zM16.5 5.2l3.2-.8 2.8 12.7-3.2.7z" />
    </template>
    <template v-else-if="name === 'users'">
      <path d="M16 20v-1.7a4.3 4.3 0 0 0-4.3-4.3H7.3A4.3 4.3 0 0 0 3 18.3V20" />
      <circle cx="9.5" cy="7" r="3" />
      <path d="M16 4.3a3 3 0 0 1 0 5.8M21 20v-1.7a4.3 4.3 0 0 0-3.2-4.1" />
    </template>
    <template v-else-if="name === 'credit-card'">
      <rect x="2.5" y="5" width="19" height="14" rx="2" />
      <path d="M2.5 10h19M6.5 15h3" />
    </template>
    <template v-else-if="name === 'menu'">
      <path d="M4 7h16M4 12h16M4 17h16" />
    </template>
    <template v-else-if="name === 'chevron-left'">
      <path d="m15 18-6-6 6-6" />
    </template>
    <template v-else-if="name === 'chevron-right'">
      <path d="m9 18 6-6-6-6" />
    </template>
    <template v-else-if="name === 'moon'">
      <path d="M20 15.2A8.5 8.5 0 0 1 8.8 4 8.5 8.5 0 1 0 20 15.2Z" />
    </template>
    <template v-else-if="name === 'sun'">
      <circle cx="12" cy="12" r="3.5" />
      <path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4" />
    </template>
    <template v-else-if="name === 'logout'">
      <path d="M10 4H5a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h5M14 8l4 4-4 4M18 12H9" />
    </template>
    <template v-else-if="name === 'arrow-up-right'">
      <path d="M7 17 17 7M8 7h9v9" />
    </template>
    <template v-else-if="name === 'plus'">
      <path d="M12 5v14M5 12h14" />
    </template>
    <template v-else-if="name === 'spark'">
      <path d="M12 2.8 13.6 8l5.2 1.6-5.2 1.6L12 16.4l-1.6-5.2-5.2-1.6L10.4 8 12 2.8Z" />
      <path d="m18.5 15 .7 2.3 2.3.7-2.3.7-.7 2.3-.7-2.3-2.3-.7 2.3-.7.7-2.3Z" />
    </template>
    <template v-else-if="name === 'file'">
      <path d="M6 2.8h8l4 4V21H6zM14 2.8v4h4M9 12h6M9 16h4" />
    </template>
    <template v-else-if="name === 'message'">
      <path d="M20 15a3 3 0 0 1-3 3H9l-5 3v-3.8A3 3 0 0 1 3 15V6a3 3 0 0 1 3-3h11a3 3 0 0 1 3 3z" />
    </template>
    <template v-else-if="name === 'database'">
      <ellipse cx="12" cy="5" rx="8" ry="3" />
      <path d="M4 5v7c0 1.7 3.6 3 8 3s8-1.3 8-3V5M4 12v7c0 1.7 3.6 3 8 3s8-1.3 8-3v-7" />
    </template>
  </svg>
</template>

<script setup lang="ts">
defineProps<{
  name:
    | 'grid'
    | 'library'
    | 'users'
    | 'credit-card'
    | 'menu'
    | 'chevron-left'
    | 'chevron-right'
    | 'moon'
    | 'sun'
    | 'logout'
    | 'arrow-up-right'
    | 'plus'
    | 'spark'
    | 'file'
    | 'message'
    | 'database'
}>()
</script>
