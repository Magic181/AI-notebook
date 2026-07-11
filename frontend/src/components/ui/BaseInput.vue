<template>
  <input
    :value="modelValue"
    class="w-full rounded-xl border border-line bg-white px-4 py-3 text-sm text-content shadow-gsm outline-none transition placeholder:text-content-secondary focus:border-primary focus:ring-4 focus:ring-primary-soft"
    @input="handleInput"
  />
</template>

<script setup lang="ts">
defineProps<{
  modelValue: string
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

function handleInput(event: Event) {
  emit('update:modelValue', (event.target as HTMLInputElement).value)
}
</script>
