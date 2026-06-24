import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useUserStore } from '@/stores/user'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/pages/Login.vue'),
    meta: { guestOnly: true },
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/pages/Register.vue'),
    meta: { guestOnly: true },
  },
  {
    path: '/',
    component: () => import('@/layouts/AppLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Home',
        component: () => import('@/pages/Home.vue'),
      },
      {
        path: 'notebook/:id',
        name: 'Notebook',
        component: () => import('@/pages/Notebook.vue'),
      },
      {
        path: 'chat/:id',
        name: 'Chat',
        component: () => import('@/pages/Chat.vue'),
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
    return { name: 'Home' }
  }
})

export default router
