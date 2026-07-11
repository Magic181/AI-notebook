<template>
  <div class="flex h-full flex-col">
    <PageHeader
      eyebrow="Starter workspace / 01"
      title="Build from a working foundation."
      description="这不是一组静态仪表盘卡片，而是 Starter Kit 的真实能力地图：哪些已经接通，哪些等待你换成自己的 adapter。"
    >
      <template #actions>
        <RouterLink to="/app/notebooks" class="kit-button kit-button-primary">
          打开 Knowledge Demo
          <AppIcon name="arrow-up-right" class="h-4 w-4" />
        </RouterLink>
      </template>
    </PageHeader>

    <div class="min-h-0 flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8">
      <section class="surface-card relative overflow-hidden p-6 sm:p-8">
        <div class="absolute -right-24 -top-24 h-72 w-72 rounded-full bg-primary-soft blur-3xl" />
        <div class="absolute bottom-0 right-[28%] h-48 w-48 rounded-full bg-accent-soft blur-3xl" />
        <div class="relative grid gap-8 lg:grid-cols-[1fr_auto] lg:items-end">
          <div>
            <p class="section-label">Foundation status</p>
            <p class="max-w-3xl text-3xl font-[730] leading-[1.02] tracking-[-0.052em] text-content sm:text-4xl lg:text-[2.8rem]">
              {{ wiredCount }} core modules are ready for your product<span class="text-primary">.</span>
            </p>
            <p class="mt-5 max-w-2xl text-sm leading-7 text-content-secondary">认证、摄取、检索、对话和部署链路可以直接运行。团队权限与计费保留清晰 UI contract，方便替换实现。</p>
            <div class="mt-6 flex flex-wrap gap-2">
              <span v-for="item in ['Auth', 'Ingestion', 'RAG', 'Operations']" :key="item" class="rounded-lg border border-line bg-white/70 px-3 py-1.5 text-xs font-medium text-content shadow-gsm">{{ item }}</span>
            </div>
          </div>
          <div class="flex min-w-48 items-center gap-4 rounded-2xl border border-line bg-white/75 p-4 shadow-gsm backdrop-blur">
            <div class="grid h-14 w-14 place-items-center rounded-full border-[5px] border-primary-soft border-t-primary text-sm font-bold text-content">{{ wiredCount }}/6</div>
            <div><p class="text-sm font-semibold text-content">Starter readiness</p><p class="mt-1 text-xs text-content-secondary">Core flow connected</p></div>
          </div>
        </div>
      </section>

      <div class="mt-4 grid grid-cols-2 gap-3 xl:grid-cols-4">
        <article v-for="metric in metrics" :key="metric.label" class="surface-card p-4 sm:p-5">
          <div class="flex items-start justify-between gap-4">
            <span class="grid h-9 w-9 place-items-center rounded-xl bg-primary-soft text-primary"><AppIcon :name="metric.icon" class="h-[18px] w-[18px]" /></span>
            <span class="h-1.5 w-1.5 rounded-full bg-status-high" />
          </div>
          <p class="mt-5 text-2xl font-bold tracking-[-0.04em] text-content">{{ metric.value }}</p>
          <p class="mt-1 text-[10px] font-medium uppercase tracking-[0.08em] text-content-secondary">{{ metric.label }}</p>
        </article>
      </div>

      <div class="mt-6 grid gap-6 xl:grid-cols-[1.25fr_0.75fr]">
        <section class="surface-card overflow-hidden">
          <div class="flex flex-col gap-3 border-b border-line p-5 sm:flex-row sm:items-end sm:justify-between sm:p-6">
            <div>
              <p class="section-label">Module map</p>
              <h2 class="text-xl font-bold tracking-[-0.035em] text-content">产品能力与替换边界</h2>
            </div>
            <span class="font-mono text-[9px] uppercase tracking-[0.13em] text-content-secondary">config/starter.ts</span>
          </div>
          <div class="grid gap-3 p-3 sm:grid-cols-2">
            <article v-for="(module, index) in starterConfig.modules" :key="module.code" class="group rounded-xl border border-transparent bg-surface p-5 transition hover:border-primary/20 hover:bg-primary-soft">
              <div class="flex items-center justify-between gap-3">
                <span class="font-mono text-[10px] font-bold text-content-secondary">{{ String(index + 1).padStart(2, '0') }}</span>
                <span class="rounded-control border px-2 py-1 font-mono text-[8px] uppercase tracking-[0.13em]" :class="module.status === 'wired' ? 'border-status-high/20 bg-green-500/10 text-status-high' : 'border-line text-content-secondary'">
                  {{ module.status }}
                </span>
              </div>
              <p class="mt-7 text-[9px] font-bold tracking-[0.12em] text-primary">{{ module.code }}</p>
              <h3 class="mt-2 font-bold tracking-[-0.02em] text-content">{{ module.title }}</h3>
              <p class="mt-2 text-xs leading-5 text-content-secondary">{{ module.description }}</p>
            </article>
          </div>
        </section>

        <div class="space-y-6">
          <section class="surface-card p-5 sm:p-6">
            <div class="flex items-center justify-between gap-3">
              <div>
                <p class="section-label">Runtime</p>
                <h2 class="text-xl font-bold tracking-[-0.035em] text-content">服务拓扑</h2>
              </div>
              <span class="h-2.5 w-2.5 rounded-full bg-status-high shadow-[0_0_0_5px_rgba(24,134,91,0.09)]" />
            </div>
            <div class="mt-6 border-t border-line">
              <div v-for="service in services" :key="service.name" class="flex items-center justify-between gap-4 border-b border-line py-3.5 last:border-0">
                <div class="flex min-w-0 items-center gap-3">
                  <span class="grid h-8 w-8 shrink-0 place-items-center rounded-lg bg-surface-secondary text-[9px] font-semibold text-content-secondary">{{ service.code }}</span>
                  <span class="truncate text-sm font-semibold text-content">{{ service.name }}</span>
                </div>
                <span class="text-[9px] font-semibold uppercase tracking-[0.09em] text-status-high">{{ service.state }}</span>
              </div>
            </div>
          </section>

          <section class="rounded-2xl border border-white/10 bg-ink p-5 text-white shadow-gmd sm:p-6">
            <p class="text-[10px] font-semibold uppercase tracking-[0.12em] text-primary">Next move</p>
            <h2 class="mt-4 text-2xl font-[700] tracking-[-0.042em]">先替换品牌配置，再决定保留哪些 feature。</h2>
            <ol class="mt-5 space-y-3 text-sm font-medium text-white/65">
              <li v-for="(step, index) in nextSteps" :key="step" class="flex gap-3 border-t border-white/10 pt-3">
                <span class="text-[10px] text-primary">0{{ index + 1 }}</span>
                <span>{{ step }}</span>
              </li>
            </ol>
          </section>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import AppIcon from '@/components/ui/AppIcon.vue'
import PageHeader from '@/components/ui/PageHeader.vue'
import { starterConfig } from '@/config/starter'
import { useNotebookStore } from '@/stores/notebook'

const notebookStore = useNotebookStore()

const wiredCount = computed(() => starterConfig.modules.filter((module) => module.status === 'wired').length)
const metrics = computed(() => [
  { label: 'wired modules', value: String(wiredCount.value), icon: 'spark' as const },
  { label: 'optional adapters', value: String(starterConfig.modules.length - wiredCount.value), icon: 'grid' as const },
  { label: 'knowledge spaces', value: String(notebookStore.notebooks.length), icon: 'library' as const },
  { label: 'compose services', value: '5', icon: 'database' as const },
])

const services = [
  { code: 'FE', name: 'Vue application', state: 'ready' },
  { code: 'API', name: 'Django API', state: 'ready' },
  { code: 'JOB', name: 'Celery worker', state: 'ready' },
  { code: 'DB', name: 'MySQL / SQLite', state: 'ready' },
  { code: 'Q', name: 'Redis queue', state: 'ready' },
]

const nextSteps = [
  '修改 config/starter.ts 的品牌与导航。',
  '删除不需要的 optional feature 页面。',
  '连接自己的模型、存储与商业化 adapter。',
]

onMounted(() => {
  if (!notebookStore.notebooks.length) {
    notebookStore.fetchNotebooks().catch(() => {})
  }
})
</script>
