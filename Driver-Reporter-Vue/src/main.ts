import './assets/main.css'
import 'bootstrap/dist/css/bootstrap.css'

import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { useAuth } from './stores/auth'

const app = createApp(App)
const { syncAuthStatus } = useAuth()

app.use(router)

void await syncAuthStatus()

app.mount('#app')
