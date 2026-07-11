import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './app/App.vue'
import router from './app/router'
import { useUserStore } from './stores/user'
import 'element-plus/theme-chalk/el-message.css'
import './styles/main.css'

async function bootstrap() {
  const app = createApp(App)
  const pinia = createPinia()

  app.use(pinia)

  const userStore = useUserStore()
  await userStore.initAuth()

  app.use(router)

  app.mount('#app')
}

bootstrap()
