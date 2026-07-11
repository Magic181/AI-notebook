<template>
  <div class="flex h-full flex-col">
    <PageHeader eyebrow="Optional feature / Team" title="Team & access adapter" description="这一页定义团队、角色、API Key 和审计事件的 UI contract。默认不伪装成已经落地的权限系统，你可以接入自己的 RBAC、SSO 或组织模型。">
      <template #actions><span class="rounded-control border border-line bg-surface-elevated px-3 py-2 font-mono text-[9px] font-bold uppercase tracking-[0.13em] text-content-secondary">UI reference</span></template>
    </PageHeader>

    <div class="min-h-0 flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8">
      <section class="grid gap-4 lg:grid-cols-3">
        <article v-for="contract in contracts" :key="contract.code" class="surface-card p-5 sm:p-6">
          <div class="flex items-center justify-between"><span class="font-mono text-[10px] font-bold tracking-[0.15em] text-primary">{{ contract.code }}</span><span class="h-2 w-2 rounded-full" :class="contract.state === 'shape ready' ? 'bg-status-high' : 'bg-status-medium'" /></div>
          <h2 class="mt-9 text-xl font-bold tracking-[-0.035em] text-content">{{ contract.title }}</h2>
          <p class="mt-3 text-sm leading-6 text-content-secondary">{{ contract.description }}</p>
          <p class="mt-6 border-t border-line pt-4 font-mono text-[9px] uppercase tracking-[0.12em] text-content-secondary">{{ contract.state }}</p>
        </article>
      </section>

      <div class="mt-6 grid gap-6 xl:grid-cols-[1.15fr_0.85fr]">
        <section class="surface-card overflow-hidden">
          <div class="border-b border-line p-5 sm:p-6"><p class="section-label">Example state</p><h2 class="text-xl font-bold tracking-[-0.035em] text-content">Member table</h2></div>
          <div class="overflow-x-auto">
            <table class="w-full min-w-[660px] text-left text-sm">
              <thead class="border-b border-line bg-surface font-mono text-[9px] uppercase tracking-[0.12em] text-content-secondary"><tr><th class="px-5 py-3 font-bold">Member</th><th class="px-5 py-3 font-bold">Role</th><th class="px-5 py-3 font-bold">State</th><th class="px-5 py-3 font-bold">Usage</th></tr></thead>
              <tbody class="divide-y divide-line">
                <tr v-for="user in users" :key="user.email" class="transition hover:bg-surface">
                  <td class="px-5 py-4"><p class="font-semibold text-content">{{ user.name }}</p><p class="mt-1 text-xs text-content-secondary">{{ user.email }}</p></td>
                  <td class="px-5 py-4 text-content-secondary">{{ user.role }}</td>
                  <td class="px-5 py-4"><span class="rounded-control bg-primary-soft px-2 py-1 font-mono text-[9px] uppercase tracking-wider text-content">{{ user.status }}</span></td>
                  <td class="px-5 py-4 font-mono text-xs text-content-secondary">{{ user.usage }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        <section class="rounded-2xl border border-ink bg-ink p-5 text-white sm:p-6">
          <p class="font-mono text-[10px] font-bold uppercase tracking-[0.15em] text-primary">Integration checklist</p>
          <h2 class="mt-4 text-2xl font-black tracking-[-0.045em]">Bring your own access model.</h2>
          <div class="mt-7 divide-y divide-white/10 border-t border-white/10">
            <div v-for="(item, index) in checklist" :key="item" class="flex gap-4 py-4"><span class="font-mono text-[10px] text-primary">0{{ index + 1 }}</span><p class="text-sm leading-6 text-white/50">{{ item }}</p></div>
          </div>
        </section>
      </div>

      <section class="surface-card mt-6 overflow-hidden">
        <div class="border-b border-line p-5 sm:p-6"><p class="section-label">Audit contract</p><h2 class="text-xl font-bold tracking-[-0.035em] text-content">Event examples</h2></div>
        <div class="grid sm:grid-cols-2 xl:grid-cols-4">
          <article v-for="log in logs" :key="log.event" class="border-b border-r border-line p-5 last:border-r-0"><p class="font-mono text-[9px] uppercase tracking-[0.13em] text-primary">{{ log.code }}</p><h3 class="mt-5 font-bold text-content">{{ log.event }}</h3><p class="mt-2 text-xs leading-5 text-content-secondary">{{ log.detail }}</p></article>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import PageHeader from '@/components/ui/PageHeader.vue'

const contracts = [
  { code: 'RBAC', title: 'Roles & scopes', description: 'Owner, admin, member and viewer states with a replaceable permission boundary.', state: 'shape ready' },
  { code: 'KEYS', title: 'API credentials', description: 'Key labels, scopes, rotation and last-used metadata for server integrations.', state: 'adapter needed' },
  { code: 'AUDIT', title: 'Audit trail', description: 'A compact event model for security, billing and content operations.', state: 'shape ready' },
]

const users = [
  { name: 'Mia Chen', email: 'mia@example.dev', role: 'Owner', status: 'Active', usage: '42k tokens' },
  { name: 'Alex Rivera', email: 'alex@example.dev', role: 'Admin', status: 'Active', usage: '31k tokens' },
  { name: 'Sam Taylor', email: 'sam@example.dev', role: 'Member', status: 'Active', usage: '18k tokens' },
  { name: 'Nora Lee', email: 'nora@example.dev', role: 'Viewer', status: 'Invited', usage: '—' },
]

const checklist = [
  'Add workspace or organization ownership to your domain models.',
  'Enforce permissions in querysets and service boundaries, not only in the UI.',
  'Connect SSO or invitation flows only if your product actually needs them.',
  'Persist audit events asynchronously and define retention up front.',
]

const logs = [
  { code: 'MODEL.UPDATED', event: 'Model route changed', detail: 'Primary chat provider switched for one workspace.' },
  { code: 'DOC.DELETED', event: 'Document removed', detail: 'An expired source was removed from a knowledge space.' },
  { code: 'KEY.ROTATED', event: 'Credential rotated', detail: 'Old ingestion key revoked and replaced.' },
  { code: 'ROLE.CHANGED', event: 'Member role changed', detail: 'A member was promoted to workspace admin.' },
]
</script>
