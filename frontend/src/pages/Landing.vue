<template>
  <div class="min-h-screen bg-surface text-content">
    <header class="fixed inset-x-0 top-0 z-20 border-b border-white/60 bg-white/82 backdrop-blur-xl">
      <div class="mx-auto flex h-16 max-w-7xl items-center justify-between px-5 lg:px-8">
        <RouterLink to="/" aria-label="AI Notebook Kit 首页">
          <StarterLogo />
        </RouterLink>
        <nav class="hidden items-center gap-7 text-sm font-medium text-content-secondary md:flex">
          <a href="#features" class="hover:text-content">能力</a>
          <a href="#stack" class="hover:text-content">技术栈</a>
          <a href="#deploy" class="hover:text-content">部署</a>
          <a href="https://github.com/Magic181/AI-notebook" class="hover:text-content" target="_blank" rel="noreferrer">
            GitHub
          </a>
        </nav>
        <div class="flex items-center gap-2">
          <RouterLink to="/login" class="gemini-btn gemini-btn-ghost hidden sm:inline-flex">
            登录
          </RouterLink>
          <RouterLink to="/register" class="gemini-btn gemini-btn-primary">
            启动 Demo
          </RouterLink>
        </div>
      </div>
    </header>

    <main>
      <section class="relative overflow-hidden pt-16">
        <img
          src="/assets/starter-hero.png"
          alt=""
          class="absolute inset-0 h-full w-full object-cover"
        />
        <div class="absolute inset-0 bg-[linear-gradient(90deg,rgba(248,250,249,0.96),rgba(248,250,249,0.78)_48%,rgba(248,250,249,0.42))]" />
        <div class="relative mx-auto grid min-h-[92vh] max-w-7xl items-center px-5 pb-14 pt-20 lg:grid-cols-[0.92fr_1.08fr] lg:px-8">
          <div class="max-w-3xl">
            <p class="mb-5 inline-flex rounded-pill border border-primary/20 bg-white/70 px-4 py-2 text-sm font-medium text-primary shadow-gsm">
              Vue + Django + RAG Starter Kit
            </p>
            <h1 class="max-w-3xl text-5xl font-semibold leading-[1.05] tracking-normal text-content sm:text-6xl lg:text-7xl">
              AI Notebook Kit
            </h1>
            <p class="mt-6 max-w-2xl text-lg leading-8 text-content-secondary">
              一个可复用的 AI 知识库启动模板，内置账号、Notebook、文档解析、OCR、视觉描述、RAG 问答、联网搜索、引用溯源和完整部署脚手架。
            </p>
            <div class="mt-8 flex flex-col gap-3 sm:flex-row">
              <RouterLink to="/register" class="gemini-btn gemini-btn-primary px-6 py-3">
                打开演示站
              </RouterLink>
              <a href="#deploy" class="gemini-btn border-line bg-white/70 px-6 py-3 text-content hover:bg-white">
                查看一键部署
              </a>
            </div>
          </div>

          <div class="mt-12 grid gap-3 rounded-card border border-white/70 bg-white/64 p-3 shadow-glg backdrop-blur-xl lg:ml-8 lg:mt-0">
            <div class="grid gap-3 md:grid-cols-[1fr_0.75fr]">
              <div class="rounded-card border border-line bg-surface-elevated p-4">
                <div class="mb-4 flex items-center justify-between">
                  <span class="text-sm font-semibold text-content">Knowledge Flow</span>
                  <span class="rounded-pill bg-primary-soft px-3 py-1 text-xs font-medium text-primary">Live</span>
                </div>
                <div class="space-y-3">
                  <div v-for="item in flowItems" :key="item" class="flex items-center gap-3 rounded-control bg-surface-secondary p-3">
                    <span class="h-2.5 w-2.5 rounded-full bg-primary" />
                    <span class="text-sm text-content-secondary">{{ item }}</span>
                  </div>
                </div>
              </div>
              <div class="rounded-card border border-line bg-surface-elevated p-4">
                <p class="text-sm font-semibold text-content">Starter Scope</p>
                <div class="mt-4 space-y-3">
                  <div v-for="metric in metrics" :key="metric.label">
                    <div class="flex items-center justify-between text-sm">
                      <span class="text-content-secondary">{{ metric.label }}</span>
                      <span class="font-semibold text-content">{{ metric.value }}</span>
                    </div>
                    <div class="mt-2 h-2 rounded-pill bg-surface-secondary">
                      <div class="h-full rounded-pill bg-primary" :style="{ width: metric.width }" />
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div class="grid gap-3 sm:grid-cols-3">
              <div v-for="capability in capabilities" :key="capability" class="rounded-card border border-line bg-surface-elevated p-4 text-sm font-medium text-content">
                {{ capability }}
              </div>
            </div>
          </div>
        </div>
      </section>

      <section id="features" class="border-t border-line bg-surface-elevated py-20">
        <div class="mx-auto max-w-7xl px-5 lg:px-8">
          <div class="max-w-2xl">
            <p class="text-sm font-semibold uppercase text-primary">Starter Kit</p>
            <h2 class="mt-3 text-3xl font-semibold tracking-normal text-content sm:text-4xl">
              不是单一应用，而是一套能继续长大的起点
            </h2>
          </div>
          <div class="mt-10 grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            <article v-for="feature in features" :key="feature.title" class="rounded-card border border-line bg-surface p-5 shadow-card-default">
              <p class="text-base font-semibold text-content">{{ feature.title }}</p>
              <p class="mt-3 text-sm leading-6 text-content-secondary">{{ feature.body }}</p>
            </article>
          </div>
        </div>
      </section>

      <section id="stack" class="bg-surface py-20">
        <div class="mx-auto grid max-w-7xl gap-8 px-5 lg:grid-cols-[0.78fr_1.22fr] lg:px-8">
          <div>
            <p class="text-sm font-semibold uppercase text-primary">Architecture</p>
            <h2 class="mt-3 text-3xl font-semibold tracking-normal text-content">前后端、任务队列和 AI 能力都已就绪</h2>
            <p class="mt-5 text-sm leading-7 text-content-secondary">
              你可以保留 Notebook 产品形态，也可以把认证、上传、解析、检索和问答模块拆出去，作为新 AI SaaS 的基础设施。
            </p>
          </div>
          <div class="grid gap-3 sm:grid-cols-2">
            <div v-for="layer in stack" :key="layer.name" class="rounded-card border border-line bg-surface-elevated p-5">
              <p class="font-semibold text-content">{{ layer.name }}</p>
              <p class="mt-2 text-sm leading-6 text-content-secondary">{{ layer.items }}</p>
            </div>
          </div>
        </div>
      </section>

      <section id="deploy" class="border-y border-line bg-surface-elevated py-20">
        <div class="mx-auto max-w-7xl px-5 lg:px-8">
          <div class="grid gap-8 lg:grid-cols-[0.8fr_1.2fr] lg:items-center">
            <div>
              <p class="text-sm font-semibold uppercase text-primary">Deploy</p>
              <h2 class="mt-3 text-3xl font-semibold tracking-normal text-content">Docker 一条命令启动全栈</h2>
              <p class="mt-5 text-sm leading-7 text-content-secondary">
                生产 Compose 包含前端 Nginx、Django API、Celery worker、MySQL 和 Redis。复制环境变量后即可在本机或服务器验证。
              </p>
            </div>
            <pre class="overflow-x-auto rounded-card border border-line bg-[#101513] p-5 text-sm leading-7 text-emerald-100 shadow-gmd"><code>cp .env.example .env
docker compose up -d --build
docker compose exec backend python manage.py createsuperuser</code></pre>
          </div>
        </div>
      </section>
    </main>

    <footer class="bg-surface py-10">
      <div class="mx-auto flex max-w-7xl flex-col gap-4 px-5 text-sm text-content-secondary sm:flex-row sm:items-center sm:justify-between lg:px-8">
        <StarterLogo subtitle="Build your own AI knowledge product" />
        <span>MIT-ready starter architecture for AI knowledge workflows.</span>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import StarterLogo from '@/components/brand/StarterLogo.vue'

const flowItems = ['Upload documents', 'Parse OCR and vision assets', 'Retrieve cited chunks', 'Answer with local or hybrid search']

const metrics = [
  { label: 'Frontend', value: 'Vue 3', width: '88%' },
  { label: 'Backend', value: 'Django', width: '82%' },
  { label: 'AI Layer', value: 'RAG', width: '76%' },
]

const capabilities = ['Auth-ready', 'RAG-ready', 'Docker-ready']

const features = [
  {
    title: '可替换的产品壳',
    body: 'Landing、演示站和应用区解耦，根路径负责展示模板价值，/app 承载真实产品体验。',
  },
  {
    title: '完整知识库闭环',
    body: 'Notebook、文档上传、解析分块、OCR、视觉描述、会话和引用来源已经串成可演示流程。',
  },
  {
    title: 'OpenAI-compatible AI 层',
    body: 'DeepSeek、Tavily、视觉模型和重试参数都集中在环境变量里，方便替换供应商。',
  },
  {
    title: '工程化目录',
    body: '前端组件、页面、状态、API 与后端 apps 保持清晰边界，便于裁剪成你自己的产品。',
  },
  {
    title: '容器化部署',
    body: '新增生产 Dockerfile、Nginx 配置和 Compose 编排，本地与服务器使用同一套启动路径。',
  },
  {
    title: '文档即入口',
    body: 'README、部署指南和文档索引围绕 Starter Kit 重新组织，第一次接手也能快速跑起来。',
  },
]

const stack = [
  { name: 'Web', items: 'Vue 3, Vite, Pinia, Vue Router, Tailwind CSS, Element Plus' },
  { name: 'API', items: 'Django 5, Django REST Framework, SimpleJWT,统一响应与限流' },
  { name: 'Jobs', items: 'Celery, Redis, eager mode for local quick start' },
  { name: 'AI', items: 'DeepSeek-compatible chat, Tavily web search, OCR, vision captions, cited RAG' },
]
</script>
