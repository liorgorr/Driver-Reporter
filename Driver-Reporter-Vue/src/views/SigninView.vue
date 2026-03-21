<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import Navbar from '../components/Nav-bar.vue'
import { useAuth } from '../stores/auth'

const router = useRouter()

const username = ref('')
const password = ref('')

const usernameValid = ref(true)
const passwordValid = ref(true)

const usernameError = ref('')
const passwordError = ref('')
const wrongInputError = ref('')
const serverError = ref('')

const showPassword = ref(false)

const isSubmitting = ref(false)
const hasAttemptedSubmit = ref(false)

const { isLoggedIn, syncAuthStatus } = useAuth()

function validateUsername(val: string) {
  if (!val) {
    usernameError.value = 'אופס! נראה ששכחת להזין את שם המשתמש שלך 😕'
    return false
  }
  return true
}

function validatePassword(val: string) {
  if (!val) {
    passwordError.value = 'אופס! נראה ששכחת להזין את הסיסמא שלך 😕'
    return false
  }
  return true
}

watch(username, async (val) => {
  if (hasAttemptedSubmit.value) usernameValid.value = validateUsername(val)
  wrongInputError.value = ''
})

watch(password, (val) => {
  if (hasAttemptedSubmit.value) passwordValid.value = validatePassword(val)
  wrongInputError.value = ''
})

async function handleSignin() {
  hasAttemptedSubmit.value = true
  isSubmitting.value = true

  usernameValid.value = validateUsername(username.value)
  passwordValid.value = validatePassword(password.value)

  if (!usernameValid.value || !passwordValid.value) {
    setTimeout(() => {
      const firstInvalid = document.querySelector('.invalid-field, .invalid-msg')
      if (firstInvalid) firstInvalid.scrollIntoView({ behavior: 'smooth', block: 'center' })
    }, 50)
    isSubmitting.value = false
    return
  }

  wrongInputError.value = ''
  serverError.value = ''

  try {
    const res = await fetch('http://localhost:8000/api/v1/auth/login/', {
      method: 'POST',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        username: username.value.trim(),
        password: password.value,
      }),
    })

    if (res.ok) {
      await syncAuthStatus()
      await router.push('/')
    } else {
      if (res.status === 401) {
        wrongInputError.value = 'אופס! נראה ששם המשתמש ו/או הסיסמא שגויים 😕'
      } else {
        const data = await res.json()
        serverError.value =
          'אופס! נראה שהשרת שלנו איבד את הדרך עם הדיווח שלך 😕\nקורה גם לטובים ביותר 😉\nנסו שוב או חזרו מאוחר יותר'
        console.error('Report submission error:', data)
        window.scrollTo({ top: 0, behavior: 'smooth' })
        setTimeout(() => {
          serverError.value = ''
        }, 15000)
      }
    }
  } catch (err) {
    serverError.value =
      'אופס! נראה שהשרת שלנו יצא לשנ"צ 😴\nגם הטובים ביותר צריכים לנוח 😉\nנסו שוב או חזרו מאוחר יותר'
    console.error('Network error:', err)
    window.scrollTo({ top: 0, behavior: 'smooth' })
    setTimeout(() => {
      serverError.value = ''
    }, 15000)
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <main>
    <Navbar />
    <section v-if="!isLoggedIn" class="signin-view" dir="rtl">
      <h1>כאן מתחברים לחשבון קיים.</h1>
      <div class="signin-content">
        <label for="signin-username" class="signin-label">שם משתשמש:</label>
        <input
          id="signin-username"
          v-model="username"
          type="text"
          class="signin-input"
          :class="{ 'invalid-field': !usernameValid }"
          @keydown.enter="handleSignin"
        />
        <div v-if="!usernameValid" class="invalid-msg">{{ usernameError }}</div>

        <label for="signin-password" class="signin-label">סיסמא:</label>
        <div class="password-wrapper">
          <input
            id="signin-password"
            v-model="password"
            :type="showPassword ? 'text' : 'password'"
            class="signin-input"
            :class="{ 'invalid-field': !passwordValid }"
            @keydown.enter="handleSignin"
          />
          <button type="button" class="eye-btn" @click="showPassword = !showPassword" tabindex="-1">
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
              <path
                d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94"
              />
              <path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19" />
              <line x1="1" y1="1" x2="23" y2="23" />
            </svg>
          </button>
        </div>
        <div v-if="!passwordValid" class="invalid-msg">{{ passwordError }}</div>
        <div v-if="wrongInputError" class="invalid-msg">{{ wrongInputError }}</div>
        <div v-if="serverError" class="error-message">{{ serverError }}</div>
        <button class="signin-btn" @click="handleSignin" :disabled="isSubmitting">
          <span>כניסה</span>
        </button>
        <p class="signup-link">
          אין לך חשבון? <RouterLink to="/signup">כאן יוצרים אחד</RouterLink>
        </p>
      </div>
    </section>
    <section v-if="isLoggedIn" class="signin-view" dir="rtl">
      <h1>נראה שאתם מחוברים 😎</h1>
    </section>
  </main>
</template>

<style scoped>
main {
  grid-column: 1 / -1;
}

.signin-view {
  position: relative;
  width: 860px;
  min-height: calc(100vh - 7rem);
  color: #d63333;
  padding: 7rem 2rem 2rem 2rem;
}

.signin-view h1 {
  font-size: 5rem;
  text-align: center;
  margin-bottom: 0.5rem;
  position: relative;
  z-index: 1;
  color: white;
}

.signin-view h1:first-of-type {
  margin-bottom: 3rem;
}

.signin-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  direction: rtl;
}

.password-wrapper {
  position: relative;
  width: 55%;
  margin-bottom: 1rem;
}

.password-wrapper .signin-input {
  width: 100%;
  margin-bottom: 0;
  padding-left: 2.5rem;
  box-sizing: border-box;
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

.signin-input {
  width: 55%;
  height: 45px;
  font-size: 1.1rem;
  padding: 0.5rem 1rem;
  margin-bottom: 1rem;
}

.signin-label {
  font-size: 1.1rem;
  color: white;
  width: 55%;
  text-align: right;
}

.signin-btn {
  background-color: #189359;
  color: #fff !important;
  border-radius: 6px;
  border-width: 0;
  padding: 0.3rem 0.6rem;
  transition: background 0.2s;
  margin-top: 2rem;
  width: 21%;
}

.signin-btn:disabled {
  background: #aaa !important;
  color: #fff !important;
  cursor: not-allowed;
  opacity: 0.7;
}

.signin-btn:hover {
  background-color: #157347;
}

.error-message {
  position: fixed;
  top: 80px;
  right: 0;
  left: 0;
  margin: 0 auto;
  z-index: 9999;
  width: fit-content;
  color: #d63333;
  font-size: 1.3rem;
  font-weight: bold;
  background: #fdecea;
  border-radius: 6px;
  padding: 0.7rem 1.2rem;
  border: 1px solid #d63333;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  text-align: center;
  white-space: pre-line;
}

.signup-link {
  color: #aaa;
  font-size: 0.9rem;
  margin-top: 0.5rem;
}

.signup-link a {
  color: #4f8ef7;
  text-decoration: none;
  font-weight: 600;
}

.signup-link a:hover {
  text-decoration: underline;
}

.invalid-field {
  border: 2px solid #d63333 !important;
}

.invalid-msg {
  color: #d63333;
  font-size: 1rem;
  margin-top: -0.7rem;
  text-align: right;
  width: 55%;
}
</style>
