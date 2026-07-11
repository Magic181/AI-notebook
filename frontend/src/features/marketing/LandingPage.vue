<template>
  <div class="min-h-screen overflow-hidden bg-surface text-content">
    <header class="fixed inset-x-0 top-0 z-30 border-b border-line/80 bg-surface/88 backdrop-blur-2xl">
      <div class="mx-auto flex h-[68px] max-w-[1320px] items-center justify-between px-5 lg:px-8">
        <RouterLink to="/" aria-label="MindBase Kit 首页">
          <StarterLogo title="MindBase Kit" subtitle="AI product starter" />
        </RouterLink>
        <nav class="hidden items-center gap-7 text-[12px] font-medium text-content-secondary lg:flex">
          <a href="#included" class="transition hover:text-primary">Included</a>
          <a href="#architecture" class="transition hover:text-primary">Architecture</a>
          <a href="#customize" class="transition hover:text-primary">Customize</a>
          <a :href="starterConfig.repositoryUrl" target="_blank" rel="noreferrer" class="transition hover:text-primary">GitHub ↗</a>
        </nav>
        <div class="flex items-center gap-2">
          <RouterLink to="/login" class="kit-button kit-button-ghost hidden sm:inline-flex">登录</RouterLink>
          <RouterLink to="/register" class="kit-button kit-button-primary">
            打开 Demo
            <AppIcon name="arrow-up-right" class="h-4 w-4" />
          </RouterLink>
        </div>
      </div>
    </header>

    <main>
      <section class="landing-grid relative border-b border-line/80 pt-[68px]">
        <div class="mx-auto grid max-w-[1320px] gap-10 px-5 py-12 lg:min-h-[760px] lg:grid-cols-[0.92fr_1.08fr] lg:items-center lg:px-8 lg:py-16">
          <div class="flex flex-col justify-center py-4 lg:py-8">
            <div>
              <div class="mb-7 flex items-center gap-3">
                <span class="h-2 w-2 rounded-full bg-primary shadow-[0_0_0_5px_var(--primary-soft)]" />
                <span class="text-[11px] font-semibold uppercase tracking-[0.12em] text-content-secondary">Full-stack AI starter kit</span>
              </div>
              <h1 class="max-w-[680px] text-[clamp(3.25rem,6.2vw,6.1rem)] font-[760] leading-[0.94] tracking-[-0.065em] text-ink dark:text-content">
                Ship the product<span class="text-primary">,</span><br />
                not the plumbing<span class="text-primary">.</span>
              </h1>
              <p class="mt-7 max-w-xl text-base leading-7 text-content-secondary sm:text-[17px] sm:leading-8">
                一套可以直接改造成你自己产品的 AI 工程底座。认证、文档摄取、RAG、流式对话、异步任务与部署边界都已经接好。
              </p>
              <div class="mt-8 flex flex-col gap-3 sm:flex-row">
                <RouterLink to="/register" class="kit-button kit-button-primary px-5 py-3">
                  从工作台开始
                  <AppIcon name="arrow-up-right" class="h-4 w-4" />
                </RouterLink>
                <a :href="starterConfig.repositoryUrl" target="_blank" rel="noreferrer" class="kit-button px-5 py-3">查看源码</a>
              </div>
            </div>

            <div class="mt-12 grid max-w-xl grid-cols-3 gap-2">
              <div v-for="stat in stats" :key="stat.label" class="rounded-xl border border-line/80 bg-white/65 px-3 py-4 shadow-gsm backdrop-blur sm:px-4">
                <p class="text-xl font-bold tracking-[-0.035em] text-content sm:text-2xl">{{ stat.value }}</p>
                <p class="mt-1 text-[9px] font-medium uppercase tracking-[0.08em] text-content-secondary">{{ stat.label }}</p>
              </div>
            </div>
          </div>

          <div class="relative flex items-center overflow-hidden rounded-[28px] bg-ink p-4 shadow-glg sm:p-6 lg:p-8">
            <div class="absolute -right-20 -top-20 h-64 w-64 rounded-full bg-primary/10 blur-3xl" />
            <div class="absolute -bottom-24 left-10 h-72 w-72 rounded-full bg-accent/10 blur-3xl" />
            <div class="kit-rise relative mx-auto w-full max-w-3xl overflow-hidden rounded-2xl border border-white/10 bg-[#242421] shadow-[0_28px_70px_-34px_rgba(0,0,0,0.85)]">
              <div class="flex h-12 items-center justify-between border-b border-white/10 px-4">
                <div class="flex gap-1.5">
                  <span class="h-2.5 w-2.5 rounded-full bg-primary" />
                  <span class="h-2.5 w-2.5 rounded-full bg-white/15" />
                  <span class="h-2.5 w-2.5 rounded-full bg-white/15" />
                </div>
                <span class="font-mono text-[9px] uppercase tracking-[0.16em] text-white/30">mindbase / workspace</span>
              </div>
              <div class="grid min-h-[470px] md:grid-cols-[180px_1fr]">
                <aside class="hidden border-r border-white/10 p-4 md:block">
                  <p class="mb-3 font-mono text-[9px] uppercase tracking-[0.16em] text-white/25">Starter map</p>
                  <div v-for="item in previewNav" :key="item.label" class="mb-1 flex items-center gap-2 rounded-md px-2.5 py-2 text-xs" :class="item.active ? 'bg-white text-ink' : 'text-white/40'">
                    <AppIcon :name="item.icon" class="h-3.5 w-3.5" />
                    <span>{{ item.label }}</span>
                  </div>
                  <div class="mt-7 border-t border-white/10 pt-4">
                    <p class="font-mono text-[9px] uppercase tracking-[0.16em] text-white/25">Adapters</p>
                    <div v-for="adapter in ['LLM provider', 'Object storage', 'Billing']" :key="adapter" class="mt-3 flex items-center gap-2 text-[11px] text-white/35">
                      <span class="h-1.5 w-1.5 rounded-full bg-primary" />
                      {{ adapter }}
                    </div>
                  </div>
                </aside>
                <div class="p-4 sm:p-6">
                  <div class="flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
                    <div>
                      <p class="font-mono text-[9px] uppercase tracking-[0.16em] text-primary">Overview / ready to fork</p>
                      <h2 class="mt-2 text-2xl font-bold tracking-[-0.04em] text-white">Your product foundation</h2>
                    </div>
                    <span class="w-fit rounded-control border border-white/15 px-2.5 py-1 font-mono text-[9px] uppercase tracking-wider text-white/45">6 modules</span>
                  </div>
                  <div class="mt-6 grid gap-3 sm:grid-cols-2">
                    <div v-for="module in previewModules" :key="module.title" class="rounded-xl border border-white/[0.08] bg-white/[0.04] p-4 transition hover:bg-white/[0.065]">
                      <div class="flex items-start justify-between gap-3">
                        <AppIcon :name="module.icon" class="h-5 w-5 text-primary" />
                        <span class="font-mono text-[8px] uppercase tracking-[0.14em] text-white/25">{{ module.code }}</span>
                      </div>
                      <p class="mt-6 text-sm font-semibold text-white">{{ module.title }}</p>
                      <p class="mt-1 text-[11px] leading-5 text-white/35">{{ module.detail }}</p>
                    </div>
                  </div>
                  <div class="mt-3 rounded-xl border border-white/10 bg-black/25 p-4 font-mono text-[10px] leading-6 text-white/45">
                    <p><span class="text-primary">$</span> cp .env.example .env</p>
                    <p><span class="text-primary">$</span> docker compose up -d --build</p>
                    <p class="text-white/20">✓ api · worker · mysql · redis · frontend</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section id="included" class="border-b border-line/80 bg-surface-elevated py-24">
        <div class="mx-auto max-w-[1320px] px-5 lg:px-8">
          <div class="grid gap-8 lg:grid-cols-[0.72fr_1.28fr]">
            <div>
              <p class="section-label">02 / Included</p>
              <h2 class="max-w-md text-4xl font-[740] leading-[1.02] tracking-[-0.05em] text-content sm:text-5xl">不是一张聊天页，是一套可拆的产品骨架。</h2>
              <p class="mt-6 max-w-md text-sm leading-7 text-content-secondary">真实能力保持独立，示例模块明确标注 adapter。你可以删掉不需要的 surface，而不用拆一团耦合代码。</p>
            </div>
            <div class="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
              <article v-for="(module, index) in starterConfig.modules" :key="module.code" class="group min-h-60 rounded-2xl border border-line bg-surface p-5 shadow-gsm transition hover:-translate-y-0.5 hover:border-primary/25 hover:bg-white hover:shadow-gmd sm:p-6">
                <div class="flex items-center justify-between">
                  <span class="font-mono text-[10px] font-bold tracking-[0.14em] text-content-secondary">{{ String(index + 1).padStart(2, '0') }}</span>
                  <span class="rounded-control border border-ink/15 px-2 py-1 font-mono text-[8px] uppercase tracking-[0.13em]" :class="module.status === 'wired' ? 'text-status-high' : 'text-content-secondary'">
                    {{ module.status }}
                  </span>
                </div>
                <p class="mt-12 text-[10px] font-bold tracking-[0.12em] text-primary">{{ module.code }}</p>
                <h3 class="mt-3 text-xl font-bold tracking-[-0.035em] text-content">{{ module.title }}</h3>
                <p class="mt-3 text-sm leading-6 text-content-secondary">{{ module.description }}</p>
              </article>
            </div>
          </div>
        </div>
      </section>

      <section id="architecture" class="border-b border-line/80 bg-surface py-24">
        <div class="mx-auto max-w-[1320px] px-5 lg:px-8">
          <div class="flex flex-col gap-5 border-b border-ink/10 pb-9 lg:flex-row lg:items-end lg:justify-between">
            <div>
              <p class="section-label">03 / Architecture</p>
              <h2 class="text-4xl font-black tracking-[-0.055em] text-content sm:text-5xl">边界先于功能。</h2>
            </div>
            <p class="max-w-xl text-sm leading-7 text-content-secondary">前端、API、异步任务、数据与外部 provider 都有清晰接缝。换模型、换对象存储或拆掉 Demo，不需要推倒重来。</p>
          </div>
          <div class="mt-10 space-y-3">
            <div v-for="(layer, index) in layers" :key="layer.name" class="grid gap-4 rounded-2xl border border-line bg-surface-elevated p-5 shadow-gsm sm:grid-cols-[72px_180px_1fr] sm:items-center sm:p-6">
              <span class="font-mono text-xs font-bold text-primary">0{{ index + 1 }}</span>
              <h3 class="text-lg font-bold tracking-[-0.03em] text-content">{{ layer.name }}</h3>
              <div class="flex flex-wrap gap-2">
                <span v-for="item in layer.items" :key="item" class="rounded-control border border-line bg-surface px-2.5 py-1.5 font-mono text-[9px] uppercase tracking-[0.1em] text-content-secondary">{{ item }}</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section id="customize" class="bg-ink py-24 text-white">
        <div class="mx-auto max-w-[1320px] px-5 lg:px-8">
          <div class="grid gap-12 lg:grid-cols-[0.75fr_1.25fr]">
            <div>
              <p class="font-mono text-[10px] font-bold uppercase tracking-[0.16em] text-primary">04 / Make it yours</p>
              <h2 class="mt-4 max-w-lg text-4xl font-[740] leading-[1.01] tracking-[-0.052em] sm:text-6xl">改品牌，换业务，接你的 adapter。</h2>
              <p class="mt-6 max-w-md text-sm leading-7 text-white/45">品牌、导航与模块声明集中在一个配置入口；页面按 feature 组织；真实接口层保持稳定。</p>
            </div>
            <div class="border-t border-white/10">
              <div v-for="step in customizeSteps" :key="step.code" class="grid gap-4 border-b border-white/10 py-7 sm:grid-cols-[64px_190px_1fr] sm:items-start">
                <span class="font-mono text-xs font-bold text-primary">{{ step.code }}</span>
                <h3 class="text-lg font-bold text-white">{{ step.title }}</h3>
                <p class="text-sm leading-6 text-white/40">{{ step.body }}</p>
              </div>
            </div>
          </div>

          <div class="mt-20 flex flex-col gap-6 rounded-[24px] bg-primary p-7 text-ink shadow-[0_24px_60px_-36px_rgba(242,100,69,0.8)] sm:flex-row sm:items-center sm:justify-between sm:p-10">
            <div>
              <p class="font-mono text-[10px] font-bold uppercase tracking-[0.16em]">Open source foundation</p>
              <h2 class="mt-3 text-3xl font-black tracking-[-0.045em] sm:text-4xl">Fork it. Break it. Make it yours.</h2>
            </div>
            <RouterLink to="/register" class="kit-button border-ink bg-ink px-5 py-3 text-white hover:border-ink hover:bg-ink-muted">
              进入工作台
              <AppIcon name="arrow-up-right" class="h-4 w-4" />
            </RouterLink>
          </div>
        </div>
      </section>
    </main>

    <footer class="border-t border-white/10 bg-ink py-8 text-white/35">
      <div class="mx-auto flex max-w-[1320px] flex-col gap-4 px-5 sm:flex-row sm:items-center sm:justify-between lg:px-8">
        <StarterLogo tone="inverse" title="MindBase Kit" subtitle="Build your own AI product" />
        <p class="font-mono text-[9px] uppercase tracking-[0.14em]">Vue · Django · RAG · Docker</p>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import StarterLogo from '@/components/brand/StarterLogo.vue'
import AppIcon from '@/components/ui/AppIcon.vue'
import { starterConfig } from '@/config/starter'

const stats = [
  { value: '6', label: 'composable modules' },
  { value: '1 cmd', label: 'production stack' },
  { value: '0', label: 'vendor lock-in' },
]

const previewNav = [
  { label: 'Overview', icon: 'grid' as const, active: true },
  { label: 'Knowledge', icon: 'library' as const },
  { label: 'Team & access', icon: 'users' as const },
  { label: 'Billing', icon: 'credit-card' as const },
]

const previewModules = [
  { code: 'RAG', title: 'Grounded answers', detail: 'Chunks, citations and hybrid retrieval.', icon: 'spark' as const },
  { code: 'INGEST', title: 'Document pipeline', detail: 'OCR, parsing and async processing.', icon: 'file' as const },
  { code: 'CHAT', title: 'Streaming chat', detail: 'Abortable SSE with conversation state.', icon: 'message' as const },
  { code: 'DATA', title: 'Portable data layer', detail: 'SQLite quick start, MySQL production.', icon: 'database' as const },
]

const layers = [
  { name: 'Experience', items: ['Vue 3', 'TypeScript', 'Pinia', 'Feature pages', 'Design tokens'] },
  { name: 'Application', items: ['Django REST', 'JWT', 'Unified errors', 'Rate limits', 'Health checks'] },
  { name: 'Intelligence', items: ['OpenAI compatible', 'RAG', 'OCR', 'Vision', 'Tavily search'] },
  { name: 'Infrastructure', items: ['Celery', 'Redis', 'MySQL', 'Nginx', 'Docker Compose'] },
]

const customizeSteps = [
  { code: '01', title: 'Configure', body: '在 config/starter.ts 集中修改品牌、导航、模块声明和仓库地址。' },
  { code: '02', title: 'Compose', body: '在 features/ 下保留需要的产品 surface，删除 Demo 不会触碰基础设施层。' },
  { code: '03', title: 'Connect', body: '把模型、存储、搜索、团队权限和计费 surface 接到自己的 provider。' },
]
</script>

<style scoped>
.landing-grid {
  background-image:
    radial-gradient(circle at 15% 12%, color-mix(in srgb, var(--primary) 8%, transparent), transparent 26rem),
    linear-gradient(to right, color-mix(in srgb, var(--text) 3.3%, transparent) 1px, transparent 1px),
    linear-gradient(to bottom, color-mix(in srgb, var(--text) 3.3%, transparent) 1px, transparent 1px);
  background-size: auto, 48px 48px, 48px 48px;
}
</style>
