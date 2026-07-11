<template>
  <button
    :class="[
      'kit-button',
      fullWidth ? 'w-full' : '',
      variantClass,
      sizeClass,
    ]"
  >
    <slot />
  </button>
</template>

<script setup lang="ts">
const props = withDefaults(
  defineProps<{
    variant?: 'primary' | 'accent' | 'tonal' | 'ghost' | 'danger'
    size?: 'sm' | 'md'
    fullWidth?: boolean
  }>(),
  {
    variant: 'primary',
    size: 'md',
    fullWidth: false,
  },
)

const variantClass = {
  primary: 'kit-button-primary',
  accent: 'kit-button-accent',
  tonal: 'kit-button-tonal',
  ghost: 'kit-button-ghost',
  danger: 'kit-button-danger',
}[props.variant]

const sizeClass = {
  sm: 'kit-button-sm',
  md: '',
}[props.size]
</script>
