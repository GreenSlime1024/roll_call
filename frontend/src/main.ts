import './assets/main.css'
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import vue3GoogleLogin from 'vue3-google-login'

const app = createApp(App)

app.use(createPinia())
app.use(vue3GoogleLogin, {
    clientId: '454220879458-3fvo26h2jqesc36hrc4t2gasir2fvpt1.apps.googleusercontent.com'
})

app.mount('#app')
