import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import App from './App.vue'
import router from './router'
import { useUserStore } from './stores/user'
import './styles/main.css'

async function bootstrap() {
  const app = createApp(App)
  const pinia = createPinia()

  app.use(pinia)

  const userStore = useUserStore()
  await userStore.initAuth()

  app.use(router)
  app.use(ElementPlus)

  app.mount('#app')
}

bootstrap()
