<template>
    <TransitionGroup name="toast-list">
        <div v-for="(toast, index) in toasts" 
             :key="toast.id"
             class="toast" 
             :class="{ 
                error: toast.type === 'error', 
                success: toast.type === 'success',
                shake: toast.type === 'error'
             }"
             :style="{ bottom: `${20 + index * 70}px` }">
            {{ toast.message }}
        </div>
    </TransitionGroup>
</template>

<script setup lang="ts">
import { ref, watch, onBeforeUnmount, nextTick } from 'vue';

interface Toast {
    id: number;
    message: string;
    type: string;
    timer?: number;
}

const props = defineProps({
    message: { type: String, required: true },
    show: { type: Boolean, default: false },
    type: { type: String, default: 'error' }
});

const toasts = ref<Toast[]>([]);
let nextId = 0;

const removeToast = (id: number) => {
    toasts.value = toasts.value.filter(t => {
        if (t.id === id && t.timer) {
            window.clearTimeout(t.timer);
        }
        return t.id !== id;
    });
};

watch(() => props.show, (newShow) => {
    if (newShow) {
        if (toasts.value.length >= 3) {
            const oldestToast = toasts.value[0];
            if (oldestToast.timer) {
                window.clearTimeout(oldestToast.timer);
            }
            toasts.value.shift();
        }

        const newToast: Toast = {
            id: nextId++,
            message: props.message,
            type: props.type
        };

        toasts.value.push(newToast);
        
        nextTick(() => {
            newToast.timer = window.setTimeout(() => {
                removeToast(newToast.id);
            }, 3000);
        });
    }
}, { flush: 'post' });

onBeforeUnmount(() => {
    toasts.value.forEach(toast => {
        if (toast.timer) {
            window.clearTimeout(toast.timer);
        }
    });
});
</script>

<style scoped>
.toast {
    position: fixed;
    right: 20px;
    padding: 15px 25px;
    border-radius: 4px;
    color: white;
    z-index: 1000;
}

.toast.error {
    background-color: #dc3545;
}

.toast.success {
    background-color: #28a745;
}

@keyframes shake {
    0%, 100% { transform: translateY(0) translateX(0); }
    10%, 30%, 50%, 70%, 90% { transform: translateY(0) translateX(-5px); }
    20%, 40%, 60%, 80% { transform: translateY(0) translateX(5px); }
}

.toast.error.show {
    animation: shake 0.6s cubic-bezier(0.36, 0.07, 0.19, 0.97) both;
}

.toast-list-enter-active,
.toast-list-leave-active {
    transition: all 0.3s ease;
}

.toast-list-enter-from {
    opacity: 0;
    transform: translateX(100%);
}

.toast-list-leave-to {
    opacity: 0;
    transform: translateX(100%);
}
</style>
