<template>
  <div class="grid min-h-screen bg-surface lg:grid-cols-[0.92fr_1.08fr]">
    <aside class="relative hidden overflow-hidden bg-ink p-10 text-white lg:flex lg:flex-col lg:justify-between xl:p-14">
      <div class="absolute -right-32 top-1/2 h-96 w-96 -translate-y-1/2 rounded-full border border-white/[0.07]"><span class="absolute inset-16 rounded-full border border-primary/30" /><span class="absolute inset-36 rounded-full bg-primary shadow-[0_0_80px_rgba(242,100,69,0.18)]" /></div>
      <div class="absolute bottom-0 left-0 h-64 w-64 rounded-full bg-accent/10 blur-3xl" />
      <RouterLink to="/" class="relative z-10 w-fit"><StarterLogo tone="inverse" title="MindBase Kit" subtitle="AI product starter" /></RouterLink>
      <div class="relative z-10 max-w-xl">
        <p class="text-[10px] font-semibold uppercase tracking-[0.13em] text-primary">Demo workspace</p>
        <h1 class="mt-5 max-w-lg text-4xl font-[720] leading-[1.02] tracking-[-0.055em] xl:text-5xl">A real product surface on top of reusable infrastructure.</h1>
        <div class="mt-9 grid grid-cols-2 gap-2">
          <div v-for="item in ['JWT auth', 'RAG pipeline', 'Streaming chat', 'Docker stack']" :key="item" class="rounded-xl border border-white/[0.07] bg-white/[0.035] p-3.5 text-[10px] font-medium uppercase tracking-[0.09em] text-white/45"><span class="mr-2 text-primary">●</span>{{ item }}</div>
        </div>
      </div>
      <p class="relative z-10 text-[9px] uppercase tracking-[0.12em] text-white/25">Fork · configure · compose · ship</p>
    </aside>

    <main class="relative flex min-h-screen items-center justify-center bg-[radial-gradient(circle_at_70%_20%,var(--primary-soft),transparent_22rem)] px-5 py-10 sm:px-8">
      <RouterLink to="/" class="absolute left-5 top-5 lg:hidden"><StarterLogo title="MindBase Kit" /></RouterLink>
      <div class="kit-rise w-full max-w-[460px] rounded-[22px] border border-line bg-white/90 p-6 shadow-glg backdrop-blur-xl sm:p-8 lg:pt-8">
        <p class="section-label">{{ eyebrow }}</p>
        <h1 class="text-[2rem] font-[710] tracking-[-0.05em] text-content sm:text-4xl">{{ title }}</h1>
        <p class="mt-3 text-sm leading-6 text-content-secondary">{{ description }}</p>
        <div class="mt-7"><slot /></div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import StarterLogo from '@/components/brand/StarterLogo.vue'

defineProps<{
  eyebrow: string
  title: string
  description: string
}>()
</script>
