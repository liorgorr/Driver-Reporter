<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import Navbar from '../components/Nav-bar.vue'
import { useAuth } from '../stores/auth'
import { getCsrfHeaders } from '../utils/csrf'
import { apiUrl } from '../utils/api'

const router = useRouter()

const username = ref('')
const password = ref('')
const confirmPassword = ref('')

const usernameValid = ref(true)
const passwordValid = ref(true)
const confirmPasswordValid = ref(true)

const usernameError = ref('')
const passwordError = ref('')
const confirmPasswordError = ref('')
const serverError = ref('')

const showPassword = ref(false)
const showConfirmPassword = ref(false)

const isSubmitting = ref(false)
const hasAttemptedSubmit = ref(false)

const { isLoggedIn, syncAuthStatus } = useAuth()

onMounted(async () => {
  await syncAuthStatus()
})

async function validateUsername(val: string) {
  if (!val.trim()) {
    usernameError.value = 'אופס! אין לך שם? 😕'
    return false
  }
  if (val.trim().length < 3) {
    usernameError.value = 'שם המשתמש חייב להכיל לפחות 3 תווים 😕'
    return false
  }
  if (val.trim().length > 150) {
    usernameError.value = 'כל הכבוד על היצירתיות אבל שם המשתמש הזה ארוך מידי 😕'
    return false
  }
  try {
    const res = await fetch(
      apiUrl(`/api/v1/auth/check-username/?username=${encodeURIComponent(val.trim())}`),
    )
    const data = await res.json()
    if (data.available === false) {
      usernameError.value = 'אופס! שם המשתמש כבר תפוס 😕 קצת מקוריות לא תזיק 😉'
      return false
    }
  } catch {}
  usernameError.value = ''
  return true
}

function validatePassword(val: string) {
  if (!val) {
    passwordError.value = 'זה אולי לא קל אבל חייבים לבחור סיסמא 😉'
    return false
  }
  if (val.length < 9) {
    passwordError.value = 'הסיסמא חייבת להכיל לפחות 9 תווים 😕'
    return false
  }
  if (!/[0-9]/.test(val)) {
    passwordError.value = 'הסיסמא חייבת להכיל לפחות מספר אחד 😕'
    return false
  }
  if (!/[a-z]/.test(val)) {
    passwordError.value = 'הסיסמא חייבת להכיל לפחות אות אחת קטנה באנגלית 😕'
    return false
  }
  if (!/[A-Z]/.test(val)) {
    passwordError.value = 'הסיסמא חייבת להכיל לפחות אות אחת גדולה באנגלית 😕'
    return false
  }
  if (val.includes(username.value)) {
    passwordError.value = 'אופס! הסיסמא לא יכולה להכיל את שם המשתמש 😕 גם אנחנו שונאים האקרים 😉'
    return false
  }
  passwordError.value = ''
  return true
}

function validateConfirm(val: string) {
  if (!val && password.value) {
    confirmPasswordError.value = 'זה אולי קצת מציק אבל חייבים לאשר את הסיסמא 😉'
    return false
  }
  if (val !== password.value) {
    confirmPasswordError.value = 'אופס! נראה שהסיסמאות לא תואמות 😕 אולי כדאי לבדוק שוב? 😉'
    return false
  }
  confirmPasswordError.value = ''
  return true
}

watch(username, async (val) => {
  if (hasAttemptedSubmit.value) {
    usernameValid.value = await validateUsername(val)
    passwordValid.value = validatePassword(password.value)
  }
})

watch(password, (val) => {
  if (hasAttemptedSubmit.value) {
    passwordValid.value = validatePassword(val)
    if (confirmPassword.value) confirmPasswordValid.value = validateConfirm(confirmPassword.value)
  }
})

watch(confirmPassword, (val) => {
  if (hasAttemptedSubmit.value) confirmPasswordValid.value = validateConfirm(val)
})

async function handleSignup() {
  await syncAuthStatus()

  if (isLoggedIn.value) {
    return
  }

  hasAttemptedSubmit.value = true
  isSubmitting.value = true

  usernameValid.value = await validateUsername(username.value)
  passwordValid.value = validatePassword(password.value)
  confirmPasswordValid.value = validateConfirm(confirmPassword.value)

  if (!usernameValid.value || !passwordValid.value || !confirmPasswordValid.value) {
    setTimeout(() => {
      const firstInvalid = document.querySelector('.invalid-field, .invalid-msg')
      if (firstInvalid) firstInvalid.scrollIntoView({ behavior: 'smooth', block: 'center' })
    }, 50)
    isSubmitting.value = false
    return
  }

  serverError.value = ''

  try {
    const signupRes = await fetch(apiUrl('/api/v1/auth/signup/'), {
      method: 'POST',
      credentials: 'include',
      headers: await getCsrfHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify({ username: username.value.trim(), password: password.value }),
    })

    const signinRes = await fetch(apiUrl('/api/v1/auth/login/'), {
      method: 'POST',
      credentials: 'include',
      headers: await getCsrfHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify({
        username: username.value.trim(),
        password: password.value,
      }),
    })

    if (signupRes.status === 201 && signinRes.ok) {
      await syncAuthStatus()
      await router.push('/')
    } else {
      const data = (await signupRes.json()) + (await signinRes.json())
      serverError.value =
        'אופס! נראה שהשרת שלנו איבד את הדרך עם נסיון ההרשמה שלך 😕\nקורה גם לטובים ביותר 😉\nנסו שוב או חזרו מאוחר יותר'
      console.error('Signup error:', data)
      window.scrollTo({ top: 0, behavior: 'smooth' })
      setTimeout(() => {
        serverError.value = ''
      }, 15000)
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
    <section v-if="!isLoggedIn" class="signup-view" dir="rtl">
      <h1>כאן יוצרים חשבון חדש.</h1>
      <div class="signup-content">
        <label for="signup-username" class="signup-label">שם משתשמש:</label>
        <input
          id="signup-username"
          type="text"
          class="signup-input"
          placeholder="לפחות 3 תווים"
          v-model="username"
          :class="{ 'invalid-field': !usernameValid }"
          @keydown.enter="handleSignup"
        />
        <div v-if="!usernameValid" class="invalid-msg">{{ usernameError }}</div>
        <label for="signup-password" class="signup-label">סיסמא:</label>
        <div class="password-wrapper">
          <input
            id="signup-password"
            :type="showPassword ? 'text' : 'password'"
            class="signup-input"
            placeholder="לפחות 9 תווים הכוללים: מספר, אות קטנה ואות גדולה"
            v-model="password"
            :class="{ 'invalid-field': !passwordValid }"
            @keydown.enter="handleSignup"
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
        <label for="signup-confirm" class="signup-label">אותה סיסמא פעם נוספת:</label>
        <div class="password-wrapper">
          <input
            id="signup-confirm"
            :type="showConfirmPassword ? 'text' : 'password'"
            class="signup-input"
            v-model="confirmPassword"
            :class="{ 'invalid-field': !confirmPasswordValid }"
            @paste.prevent
            @keydown.enter="handleSignup"
          />
          <button
            type="button"
            class="eye-btn"
            @click="showConfirmPassword = !showConfirmPassword"
            tabindex="-1"
          >
            <svg
              v-if="!showConfirmPassword"
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
        <div v-if="!confirmPasswordValid" class="invalid-msg">{{ confirmPasswordError }}</div>
        <div v-if="serverError" class="error-message">{{ serverError }}</div>
        <button class="signup-btn" @click="handleSignup" :disabled="isSubmitting">הרשמה</button>
        <p class="signup-link">
          יש לך כבר חשבון? <RouterLink to="/signin">כאן נכנסים אליו</RouterLink>
        </p>
      </div>
    </section>
    <section v-else class="signup-view" dir="rtl">
      <h1>נראה שאתם כבר מחוברים 😎</h1>
    </section>
  </main>
</template>

<style scoped>
main {
  grid-column: 1 / -1;
}

.signup-view {
  position: relative;
  min-width: 960px;
  min-height: calc(100vh - 7rem);
  padding: 7rem 2rem 2rem 2rem;
}

.signup-view h1 {
  font-size: 5rem;
  text-align: center;
  margin-bottom: 0.5rem;
  position: relative;
  z-index: 1;
  color: white;
}

.signup-view h1:first-of-type {
  margin-bottom: 3rem;
}

.signup-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  direction: rtl;
}

.password-wrapper {
  position: relative;
  width: 50%;
  margin-bottom: 0.5rem;
}

.password-wrapper .signup-input {
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

.signup-input {
  width: 50%;
  height: 45px;
  font-size: 1.1rem;
  padding: 0.5rem 1rem;
  margin-bottom: 0.5rem;
}

.signup-label {
  font-size: 1.1rem;
  color: white;
  width: 50%;
  text-align: right;
}

.signup-btn {
  background-color: #189359;
  color: #fff !important;
  border-radius: 6px;
  border-width: 0;
  padding: 0.3rem 0.6rem;
  transition: background 0.2s;
  margin-top: 2rem;
  width: 20%;
}

.signup-btn:disabled {
  background: #aaa !important;
  color: #fff !important;
  cursor: not-allowed;
  opacity: 0.7;
}

.signup-btn:hover {
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
  width: 50%;
}
</style>
