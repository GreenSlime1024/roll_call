<template>
    <div class="login-page">
        <h1>Roll Call System</h1>
        <p>Please login with your Google account</p>
        <Toast 
            :message="toastMessage" 
            :show="showToast"
            :type="toastType"
        />
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import Toast from './Toast.vue'
import { googleOneTap } from 'vue3-google-login'

const emit = defineEmits(['login-success'])
const toastMessage = ref('')
const showToast = ref(false)
const toastType = ref('error')

onMounted(() => {
    setTimeout(() => {
        const logoutMessage = sessionStorage.getItem('logout_message')
        if (logoutMessage) {
            toastMessage.value = logoutMessage
            toastType.value = 'success'
            showToast.value = true
            sessionStorage.removeItem('logout_message')
        }
        
        googleOneTap()
            .then((response: any) => {
                callback(response)
            })
            .catch((error: any) => {
                console.log('One Tap Error:', error)
            })
    }, 100)
})

function showToastMessage(message: string, type: 'error' | 'success' = 'error') {
    toastMessage.value = message
    toastType.value = type
    showToast.value = true
    setTimeout(() => {
        showToast.value = false
    }, 3000)
}

const callback = async (response: any) => {
    try {
        const result = await fetch('/api/login', {  // Note the leading slash
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ credential: response.credential }),
        })
        
        if (!result.ok) {
            const error = await result.json()
            throw new Error(error.detail || 'Access denied. Please use your school account.')
        }
        
        const data = await result.json()
        localStorage.setItem('jwt_token', data.token)
        emit('login-success')
    } catch (error: any) {
        const errorMessage = error.message.includes('failed to fetch') 
            ? 'Unable to connect to the server. Please check your internet connection.'
            : error.message
        showToastMessage(errorMessage)
        console.error('Login error:', error)
    }
}
</script>

<style scoped>
.login-page {
    height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 20px;
    text-align: center;
    background-color: var(--background-color);
    color: var(--text-primary);
}

h1 {
    color: var(--primary-color);
    margin-bottom: 0.5rem;
}

p {
    color: var(--text-secondary);
    font-size: 1.1rem;
}
</style>
