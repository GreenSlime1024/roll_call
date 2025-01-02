<template>
    <div>
        <div class="row header" v-if="isHeader">
            <div class="col sortable" @click="$emit('sort', 'student_id')">
                Student ID
                <span class="sort-icon" v-if="sortField === 'student_id'">
                    {{ sortOrder === 'asc' ? '▲' : '▼' }}
                </span>
            </div>
            <div class="col sortable" @click="$emit('sort', 'rfid_id')">
                RFID
                <span class="sort-icon" v-if="sortField === 'rfid_id'">
                    {{ sortOrder === 'asc' ? '▲' : '▼' }}
                </span>
            </div>
            <div class="col sortable" @click="$emit('sort', 'present')">
                Present
                <span class="sort-icon" v-if="sortField === 'present'">
                    {{ sortOrder === 'asc' ? '▲' : '▼' }}
                </span>
            </div>
        </div>
        <div class="row" v-else>
            <div class="col">
                <input
                    type="number"
                    v-model="localStudentId"
                    @blur="updateStudentId"
                    @keyup.enter="handleEnter"
                    :disabled="!isAdmin"
                />
            </div>

            <div class="col"
                :style="{ cursor: isAdmin ? 'pointer' : 'default' }"
                @click="handleRfidClick">{{ rfid_id }}
            </div>
            
            <div class="col">
                <input
                    type="checkbox"
                    v-model="localPresent"
                    :name="'checkbox-' + (student_id || rfid_id)"
                    @change="updatePresent"
                    :disabled="!isAdmin"
                    :style="{ cursor: isAdmin ? 'pointer' : 'not-allowed' }"
                />
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

const props = defineProps({
    student_id: { type: [Number, null], default: null },
    rfid_id: { type: String, required: true },
    present: { type: Boolean, default: false },
    isAdmin: { type: Boolean, default: false },
    isHeader: { type: Boolean, default: false },
    sortField: { type: String, default: '' },
    sortOrder: { type: String, default: 'asc' },
})

const emit = defineEmits(['updatePerson', 'sort'])
const localPresent = ref(props.present)
const localStudentId = ref(props.student_id)


function updatePerson(type: string) {
    if (String(localStudentId.value) === "") {
        localStudentId.value = null
    }
    console.log('updatePerson', localPresent.value, localStudentId.value, props.rfid_id, type)
    emit('updatePerson', localPresent.value, localStudentId.value, props.rfid_id, type)
}

function updatePresent() {
    updatePerson('present')
}

function updatePresentFromOthers() {
    localPresent.value = !localPresent.value
    updatePerson('present')
}

function updateStudentId() {
    updatePerson('student_id')
}

function handleEnter(event: KeyboardEvent) {
    (event.target as HTMLInputElement).blur()
}

function handleRfidClick() {
    if (props.isAdmin) {
        updatePresentFromOthers()
    }
}

watch(
    () => props.student_id,
    (newVal) => {
        localStudentId.value = newVal
    }
)

watch(
    () => props.present,
    (newVal) => {
        localPresent.value = newVal
    }
)

</script>

<style scoped>
.row {
    display: flex;
    justify-content: space-between;
    padding: 10px;
    background-color: #131313;
    overflow: hidden; /* Prevent overflow */
}

.row:nth-child(even) {
    background-color: #303030;
}

.row:hover {
    background-color: #284e22;
}

.col {
    flex: 1;
    text-align: center;
    overflow: hidden; /* Prevent overflow */
    white-space: nowrap; /* Prevent text wrapping */
    text-overflow: ellipsis; /* Add ellipsis for overflowed text */
}

input[type="number"] {
    width: 20%;
    padding: 5px;
    font-size: 1rem;
    text-align: center;
    border: 1px solid #ccc;
    border-radius: 4px;
    background-color: #2c2c2c;
    color: #ffffff;
}

input[type="number"]:disabled {
    opacity: 1;
    color: #cccccc;
    cursor: not-allowed;
}

input[type="checkbox"] {
    width: 25px;
    height: 25px;
    cursor: pointer;
}

.header {
    font-weight: bold;
    background-color: #1a1a1a !important;
    border-bottom: 2px solid #404040;
}

.header:hover {
    background-color: #1a1a1a !important;
}

.sortable {
    cursor: pointer;
    user-select: none;
}

.sortable:hover {
    color: #4CAF50;
}

.sort-icon {
    margin-left: 5px;
    font-size: 0.8em;
}
</style>