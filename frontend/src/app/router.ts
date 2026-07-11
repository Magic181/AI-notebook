import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useUserStore } from '@/stores/user'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Landing',
    component: () => import('@/features/marketing/LandingPage.vue'),
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/features/auth/LoginPage.vue'),
    meta: { guestOnly: true },
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/features/auth/RegisterPage.vue'),
    meta: { guestOnly: true },
  },
  {
    path: '/app',
    component: () => import('@/app/layouts/AppShell.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Dashboard',
        component: () => import('@/features/dashboard/DashboardPage.vue'),
      },
      {
        path: 'notebooks',
        name: 'KnowledgeBase',
        component: () => import('@/features/knowledge/KnowledgeBasePage.vue'),
      },
      {
        path: 'notebook/:id',
        name: 'Notebook',
        component: () => import('@/features/knowledge/NotebookPage.vue'),
      },
      {
        path: 'chat/:id',
        name: 'Chat',
        component: () => import('@/features/chat/ChatPage.vue'),
      },
      {
        path: 'admin',
        name: 'AdminConsole',
        component: () => import('@/features/admin/AdminPage.vue'),
      },
      {
        path: 'billing',
        name: 'Billing',
        component: () => import('@/features/billing/BillingPage.vue'),
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach(async (to) => {
  const userStore = useUserStore()

  if (!userStore.authReady) {
    await userStore.initAuth()
  }

  if (to.meta.requiresAuth && !userStore.isLoggedIn) {
    return { name: 'Login', query: { redirect: to.fullPath } }
  }

  if (to.meta.guestOnly && userStore.isLoggedIn) {
    return { name: 'Dashboard' }
  }
})

export default router
