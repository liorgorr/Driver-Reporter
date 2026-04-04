<script setup lang="ts">
import { ref } from 'vue'

const props = withDefaults(
  defineProps<{
    modelValue: string
    id: string
    placeholder?: string
    invalid?: boolean
    preventPaste?: boolean
    width?: string
    marginBottom?: string
    placeholderFontSize?: string
  }>(),
  {
    placeholder: '',
    invalid: false,
    preventPaste: false,
    width: '50%',
    marginBottom: '1rem',
    placeholderFontSize: '1rem',
  },
)

const emit = defineEmits<{
  (event: 'update:modelValue', value: string): void
  (event: 'enter'): void
}>()

const showPassword = ref(false)

function updateValue(event: Event): void {
  emit('update:modelValue', (event.target as HTMLInputElement).value)
}

function handlePaste(event: ClipboardEvent): void {
  if (props.preventPaste) {
    event.preventDefault()
  }
}
</script>

<template>
  <div class="password-wrapper" :style="{ width, marginBottom }">
    <input
      :id="id"
      :value="modelValue"
      :type="showPassword ? 'text' : 'password'"
      class="password-input"
      :class="{ 'invalid-field': invalid }"
      :placeholder="placeholder"
      :style="{ '--password-placeholder-size': placeholderFontSize }"
      @input="updateValue"
      @keydown.enter="emit('enter')"
      @paste="handlePaste"
    />
    <button
      type="button"
      class="eye-btn"
      tabindex="-1"
      @click="showPassword = !showPassword"
    >
      <svg
        v-if="!showPassword"
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
      >
        <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
        <circle cx="12" cy="12" r="3" />
      </svg>
      <svg
        v-else
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
      >
        <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94" />
        <path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19" />
        <line x1="1" y1="1" x2="23" y2="23" />
      </svg>
    </button>
  </div>
</template>

<style scoped>
.password-wrapper {
  position: relative;
}

.password-input {
  width: 100%;
  height: 45px;
  font-size: 1.1rem;
  padding: 0.5rem 1rem;
  padding-left: 2.5rem;
  margin-bottom: 0;
  box-sizing: border-box;
}

.password-input.invalid-field {
  border: 2px solid #d63333 !important;
}

.password-input::placeholder {
  font-size: var(--password-placeholder-size);
}

.eye-btn {
  position: absolute;
  left: 0.6rem;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  cursor: pointer;
  padding: 0;
  color: #888;
  display: flex;
  align-items: center;
}

.eye-btn:hover {
  color: #333;
}

.eye-btn svg {
  width: 20px;
  height: 20px;
}
</style>
