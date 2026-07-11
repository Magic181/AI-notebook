export type NavigationIcon =
  | 'grid'
  | 'library'
  | 'users'
  | 'credit-card'

export interface StarterNavigationItem {
  label: string
  to: string
  icon: NavigationIcon
  match: string[]
  optional?: boolean
}

export const starterConfig = {
  brand: {
    name: 'MindBase',
    suffix: 'Kit',
    descriptor: 'AI product starter',
  },
  repositoryUrl: 'https://github.com/Magic181/mindbase-kit',
  navigation: [
    { label: 'Overview', to: '/app', icon: 'grid', match: ['/app'] },
    {
      label: 'Knowledge',
      to: '/app/notebooks',
      icon: 'library',
      match: ['/app/notebooks', '/app/notebook', '/app/chat'],
    },
    { label: 'Team & access', to: '/app/admin', icon: 'users', match: ['/app/admin'], optional: true },
    { label: 'Billing', to: '/app/billing', icon: 'credit-card', match: ['/app/billing'], optional: true },
  ] satisfies StarterNavigationItem[],
  modules: [
    { code: 'AUTH', title: 'Authentication', description: 'JWT registration, login, refresh and route guards.', status: 'wired' },
    { code: 'KNOW', title: 'Knowledge ingestion', description: 'Upload, parse, OCR, chunk and index documents.', status: 'wired' },
    { code: 'RAG', title: 'Grounded chat', description: 'Streaming answers, citations and hybrid web search.', status: 'wired' },
    { code: 'OPS', title: 'Operations', description: 'Docker, Celery, Redis, MySQL and health checks.', status: 'wired' },
    { code: 'TEAM', title: 'Team & roles', description: 'A UI contract ready for your permission adapter.', status: 'adapter' },
    { code: 'PAY', title: 'Billing', description: 'A Stripe-ready surface with usage and plan states.', status: 'adapter' },
  ],
} as const
