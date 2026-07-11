<template>
  <div class="flex h-full flex-col">
    <PageHeader eyebrow="Optional feature / Billing" title="Billing adapter" description="套餐、用量与账单事件只定义产品界面和状态模型。接入 Stripe、Lemon Squeezy 或自有计费之前，不展示会误导用户的假支付操作。">
      <template #actions><span class="rounded-control border border-line bg-surface-elevated px-3 py-2 font-mono text-[9px] font-bold uppercase tracking-[0.13em] text-content-secondary">Provider agnostic</span></template>
    </PageHeader>

    <div class="min-h-0 flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8">
      <section class="grid gap-4 lg:grid-cols-3">
        <article v-for="plan in plans" :key="plan.name" class="relative overflow-hidden rounded-2xl border p-5 sm:p-6" :class="plan.featured ? 'border-ink bg-ink text-white' : 'border-line bg-surface-elevated text-content'">
          <div class="flex items-center justify-between gap-3"><span class="font-mono text-[9px] font-bold uppercase tracking-[0.14em]" :class="plan.featured ? 'text-primary' : 'text-content-secondary'">{{ plan.code }}</span><span v-if="plan.featured" class="rounded-control border border-white/15 px-2 py-1 font-mono text-[8px] uppercase tracking-wider text-white/45">example current</span></div>
          <h2 class="mt-10 text-2xl font-black tracking-[-0.045em]">{{ plan.name }}</h2>
          <p class="mt-3 text-sm leading-6" :class="plan.featured ? 'text-white/45' : 'text-content-secondary'">{{ plan.description }}</p>
          <ul class="mt-7 space-y-3 border-t pt-5 text-sm" :class="plan.featured ? 'border-white/10 text-white/60' : 'border-line text-content-secondary'"><li v-for="feature in plan.features" :key="feature" class="flex gap-3"><span class="text-primary">—</span>{{ feature }}</li></ul>
        </article>
      </section>

      <div class="mt-6 grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
        <section class="surface-card p-5 sm:p-6">
          <div class="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between"><div><p class="section-label">Usage contract</p><h2 class="text-xl font-bold tracking-[-0.035em] text-content">Metered dimensions</h2></div><span class="font-mono text-[9px] uppercase tracking-[0.13em] text-content-secondary">Example cycle</span></div>
          <div class="mt-7 space-y-6">
            <div v-for="item in usage" :key="item.label"><div class="flex items-center justify-between gap-3"><span class="text-sm font-semibold text-content">{{ item.label }}</span><span class="font-mono text-[10px] text-content-secondary">{{ item.value }}</span></div><div class="mt-2 h-2 overflow-hidden rounded-sm bg-surface-secondary"><div class="h-full bg-primary" :style="{ width: item.width }" /></div></div>
          </div>
        </section>

        <section class="surface-card overflow-hidden">
          <div class="border-b border-line p-5 sm:p-6"><p class="section-label">Implementation</p><h2 class="text-xl font-bold tracking-[-0.035em] text-content">What remains</h2></div>
          <div class="divide-y divide-line"><div v-for="(item, index) in implementation" :key="item" class="flex gap-4 p-5"><span class="font-mono text-[10px] font-bold text-primary">0{{ index + 1 }}</span><p class="text-sm leading-6 text-content-secondary">{{ item }}</p></div></div>
        </section>
      </div>

      <section class="surface-card mt-6 p-5 sm:p-6">
        <p class="section-label">Event model</p>
        <div class="mt-4 grid gap-3 sm:grid-cols-3"><article v-for="event in events" :key="event.name" class="rounded-xl border border-line bg-surface p-4"><p class="font-mono text-[9px] uppercase tracking-[0.13em] text-primary">{{ event.name }}</p><p class="mt-4 text-sm leading-6 text-content-secondary">{{ event.detail }}</p></article></div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import PageHeader from '@/components/ui/PageHeader.vue'

const plans = [
  { code: 'FREE', name: 'Open source', description: '适合本地体验、原型验证与二次开发。', features: ['SQLite quick start', 'Local knowledge demo', 'Community deployment'] },
  { code: 'TEAM', name: 'Team product', description: '一个示例套餐状态，用来承接团队、用量和商业化 UI。', features: ['Workspace seats', 'Usage dashboard', 'Admin surface'], featured: true },
  { code: 'CUSTOM', name: 'Enterprise adapter', description: '为 SSO、私有模型、审计与定制存储预留接口。', features: ['SSO boundary', 'Private providers', 'Custom retention'] },
]

const usage = [
  { label: 'AI credits', value: '72,400 / 100,000', width: '72%' },
  { label: 'Storage', value: '18.4 GB / 100 GB', width: '18%' },
  { label: 'Seats', value: '8 / 20', width: '40%' },
  { label: 'Web searches', value: '1,240 / 5,000', width: '25%' },
]

const implementation = [
  'Choose a billing provider and make it the source of truth.',
  'Persist customer, subscription, price and entitlement identifiers.',
  'Verify webhooks, make handlers idempotent and replay-safe.',
  'Gate features from server-side entitlements rather than UI state.',
]

const events = [
  { name: 'subscription.updated', detail: '同步套餐、状态、当前周期和取消时间。' },
  { name: 'usage.reported', detail: '按稳定维度记录可计费用量。' },
  { name: 'invoice.failed', detail: '触发宽限期、通知与权限降级策略。' },
]
</script>
