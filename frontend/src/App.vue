<template>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <LoginPage v-if="!isAuthenticated" @login-success="handleLoginSuccess" />
    <div v-else>
        <div class="header">
            <div style="margin-left: auto;" class="user-controls">
                <img v-if="userAvatar" :src="userAvatar" class="avatar" alt="User avatar" />
                <span class="user-email">{{ userEmail }}</span>
                <button class="logout-btn" @click="handleLogout">Logout</button>
            </div>
        </div>
        <h2>Members</h2>
        <div class="row-container">
            <Row 
                :is-header="true" 
                :rfid_id="''" 
                :is-admin="isAdmin"
                :sort-field="sortField"
                :sort-order="sortOrder"
                @sort="handleSort"
            />
            <Row v-for="person in sortedPeopleWithId" 
                :student_id="person.student_id" 
                :rfid_id="person.rfid_id" 
                :present="person.present" 
                :is-admin="isAdmin" 
                @update-person="updatePerson"
            />
        </div>

        <h2>Guests</h2>
        <div class="row-container">
            <Row 
                :is-header="true" 
                :rfid_id="''" 
                :is-admin="isAdmin"
                :sort-field="sortField"
                :sort-order="sortOrder"
                @sort="handleSort"
            />
            <Row v-for="person in sortedPeopleWithoutId" 
                :student_id="person.student_id" 
                :rfid_id="person.rfid_id" 
                :present="person.present" 
                :is-admin="isAdmin" 
                @update-person="updatePerson" 
            />
        </div>
        <Toast 
            :message="toastMessage" 
            :show="showToast"
            :type="toastType"
        />
    </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, nextTick } from 'vue'
import Row from './components/Row.vue'
import LoginPage from './components/LoginPage.vue'
import Toast from './components/Toast.vue'

interface Person {
    student_id: number | null
    rfid_id: string
    present: boolean
}

const people = ref<Person[]>([])
const isAuthenticated = ref(!!localStorage.getItem('jwt_token'))
const userEmail = ref('')
const userAvatar = ref('')
const isAdmin = ref(false)
const errorMsg = ref('')

const toastMessage = ref('')
const showToast = ref(false)
const toastType = ref('error')

function showToastMessage(message: string, type: 'error' | 'success' = 'error') {
    showToast.value = false
    setTimeout(() => {
        toastMessage.value = message
        toastType.value = type
        showToast.value = true
    }, 0)
}

const checkAdminStatus = async () => {
    try {
        const response = await fetch('api/check-admin', {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('jwt_token')}`
            }
        });
        const data = await response.json();
        isAdmin.value = data.is_admin;
    } catch (error) {
        console.error('Error checking admin status:', error);
        isAdmin.value = false;
    }
}

const initializeUserFromToken = () => {
    const token = localStorage.getItem('jwt_token')
    if (token) {
        try {
            const payload = JSON.parse(atob(token.split('.')[1]))
            userEmail.value = payload.email
            userAvatar.value = payload.picture
            checkAdminStatus()
            return true
        } catch (error) {
            console.error('Failed to parse JWT token:', error)
            localStorage.removeItem('jwt_token')
            isAuthenticated.value = false
            return false
        }
    }
    return false
}

const handleLoginSuccess = () => {
    isAuthenticated.value = true
    if (initializeUserFromToken()) {
        fetchPeople()
        if (!(window as any).peopleInterval) {
            (window as any).peopleInterval = setInterval(fetchPeople, 1000)
        }
        nextTick(() => {
            showToastMessage(`Welcome back, ${userEmail.value}!`, 'success')
        })
    }
}

const handleLogout = () => {
    sessionStorage.setItem('logout_message', 'Logged out successfully')
    
    if ((window as any).peopleInterval) {
        clearInterval((window as any).peopleInterval)
        delete (window as any).peopleInterval
    }

    isAuthenticated.value = false
    
    nextTick(() => {
        localStorage.removeItem('jwt_token')
        userEmail.value = ''
        userAvatar.value = ''
    })
}

function getErrorMessage(error: any): string {
    if (error.message.includes('failed to fetch')) {
        return 'Connection lost. Please check your internet connection.'
    }
    if (error.message.includes('JWT')) {
        return 'Your session has expired. Please login again.'
    }
    return error.message || 'An unexpected error occurred.'
}

const updatePerson = (present: boolean, student_id: number | null, rfid_id: string, type: string) => {
    if (!isAdmin.value) {
        showToastMessage("Access denied. Only administrators can modify records.")
        return
    }
    
    fetch('api/person', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('jwt_token')}`
        },
        body: JSON.stringify({ present, student_id, rfid_id, type }),
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(err => {
                throw new Error(err.detail || `Failed to update ${type}`)
            })
        }
        return response.json()
    })
    .then(() => {
        fetchPeople()
        const actionType = type === 'present' ? 'attendance' : 'student ID'
        showToastMessage(`Successfully updated ${actionType}`, 'success')
    })
    .catch(error => {
        showToastMessage(getErrorMessage(error))
        console.error('Update error:', error)
    })
}

const fetchPeople = () => {
    fetch('api/people', {
        headers: {
            'Authorization': `Bearer ${localStorage.getItem('jwt_token')}`
        }
    })
    .then(response => response.json())
    .then(data => {
        people.value = data.people
    })
    .catch(error => {
        showToastMessage(getErrorMessage(error))
        if (error.message.includes('JWT')) {
            handleLogout()
        }
        console.error('Fetch error:', error)
    })
}

onMounted(() => {
    const token = localStorage.getItem('jwt_token')
    if (token) {
        isAuthenticated.value = true
        if (initializeUserFromToken()) {
            fetchPeople()
            if (!(window as any).peopleInterval) {
                (window as any).peopleInterval = setInterval(fetchPeople, 1000)
            }
        } else {
            isAuthenticated.value = false
        }
    }
})

const people_with_id = computed(() => people.value.filter(person => person.student_id !== null).sort((a, b) => (a.student_id ?? 0) - (b.student_id ?? 0))
)
const people_without_id = computed(() => people.value.filter(person => person.student_id === null))

const sortField = ref('')
const sortOrder = ref('asc')

const handleSort = (field: string) => {
    if (sortField.value === field) {
        sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
    } else {
        sortField.value = field
        sortOrder.value = 'asc'
    }
}

const sortedPeopleWithId = computed(() => {
    const sorted = [...people_with_id.value]
    if (!sortField.value) return sorted

    return sorted.sort((a, b) => {
        const aValue = a[sortField.value as keyof Person]
        const bValue = b[sortField.value as keyof Person]
        
        if (aValue === null) return 1
        if (bValue === null) return -1
        
        const compare = aValue < bValue ? -1 : aValue > bValue ? 1 : 0
        return sortOrder.value === 'asc' ? compare : -compare
    })
})

const sortedPeopleWithoutId = computed(() => {
    const sorted = [...people_without_id.value]
    if (!sortField.value) return sorted

    return sorted.sort((a, b) => {
        const aValue = a[sortField.value as keyof Person]
        const bValue = b[sortField.value as keyof Person]
        
        if (aValue === null) return 1
        if (bValue === null) return -1
        
        const compare = aValue < bValue ? -1 : aValue > bValue ? 1 : 0
        return sortOrder.value === 'asc' ? compare : -compare
    })
})
</script>

<style>
.row-container {
    display: flex;
    flex-direction: column;
    width: 100%;
    max-width: 100vw;
    overflow-x: hidden;
    overflow-y: auto;
    box-sizing: border-box;
}

body {
    margin: 0;
    padding: 0;
    width: 100%;
    max-width: 100vw;
    overflow-x: hidden;
    box-sizing: border-box;
}

.header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 20px;
    width: 100%;
    max-width: 100vw;
    box-sizing: border-box;
}

.logout-btn {
    background-color: #dc3545;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    cursor: pointer;
}

.logout-btn:hover {
    background-color: #c82333;
}

.user-controls {
    display: flex;
    align-items: center;
    gap: 12px;
}

.user-email {
    color: #666;
    font-size: 0.9em;
}

.avatar {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    object-fit: cover;
}
</style>