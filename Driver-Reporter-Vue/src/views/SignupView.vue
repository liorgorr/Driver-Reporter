<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import Navbar from '../components/Nav-bar.vue'
import PasswordField from '../components/PasswordField.vue'
import { useAuth } from '../stores/auth'
import { getCsrfHeaders } from '../utils/csrf'
import { apiUrl } from '../utils/api'
import { usePasswordValidation } from '../composables/usePasswordValidation'
import { useFormUi } from '../composables/useFormUi'

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

const isSubmitting = ref(false)
const hasAttemptedSubmit = ref(false)

const { isLoggedIn, syncAuthStatus } = useAuth()
const { validatePassword, validateConfirmPassword } = usePasswordValidation(
  username,
  password,
  passwordError,
  confirmPasswordError,
)
const { scrollToFirstInvalid, showServerError } = useFormUi()

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

watch(username, async (val) => {
  if (hasAttemptedSubmit.value) {
    usernameValid.value = await validateUsername(val)
    passwordValid.value = validatePassword(password.value)
  }
})

watch(password, (val) => {
  if (hasAttemptedSubmit.value) {
    passwordValid.value = validatePassword(val)
    if (confirmPassword.value) {
      confirmPasswordValid.value = validateConfirmPassword(confirmPassword.value)
    }
  }
})

watch(confirmPassword, (val) => {
  if (hasAttemptedSubmit.value) confirmPasswordValid.value = validateConfirmPassword(val)
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
  confirmPasswordValid.value = validateConfirmPassword(confirmPassword.value)

  if (!usernameValid.value || !passwordValid.value || !confirmPasswordValid.value) {
    scrollToFirstInvalid()
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

    if (signupRes.status !== 201) {
      const signupError = await signupRes.json()
      showServerError(
        serverError,
        'אופס! נראה שהשרת שלנו איבד את הדרך עם נסיון ההרשמה שלך 😕\nקורה גם לטובים ביותר 😉\nנסו שוב או חזרו מאוחר יותר',
      )
      console.error('Signup error:', signupError)
      return
    }

    const signinRes = await fetch(apiUrl('/api/v1/auth/login/'), {
      method: 'POST',
      credentials: 'include',
      headers: await getCsrfHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify({
        username: username.value.trim(),
        password: password.value,
      }),
    })

    if (signinRes.ok) {
      await syncAuthStatus()
      await router.push('/')
    } else {
      const signinError = await signinRes.json()
      showServerError(
        serverError,
        'אופס! נראה שהשרת שלנו איבד את הדרך עם נסיון ההתחברות שלך אחרי ההרשמה 😕\nקורה גם לטובים ביותר 😉\nנסו שוב או חזרו מאוחר יותר',
      )
      console.error('Signin after signup error:', signinError)
    }
  } catch (err) {
    showServerError(
      serverError,
      'אופס! נראה שהשרת שלנו יצא לשנ"צ 😴\nגם הטובים ביותר צריכים לנוח 😉\nנסו שוב או חזרו מאוחר יותר',
    )
    console.error('Network error:', err)
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
        <PasswordField
          id="signup-password"
          v-model="password"
          placeholder="לפחות 9 תווים הכוללים: מספר, אות קטנה ואות גדולה"
          :invalid="!passwordValid"
          marginBottom="0.5rem"
          @enter="handleSignup"
        />
        <div v-if="!passwordValid" class="invalid-msg">{{ passwordError }}</div>
        <label for="signup-confirm" class="signup-label">אותה סיסמא פעם נוספת:</label>
        <PasswordField
          id="signup-confirm"
          v-model="confirmPassword"
          :invalid="!confirmPasswordValid"
          :preventPaste="true"
          marginBottom="0.5rem"
          @enter="handleSignup"
        />
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
@import '../assets/form-feedback.css';

main {
  grid-column: 1 / -1;
}

.signup-view {
  position: relative;
  min-width: 960px;
  min-height: calc(100vh - 7rem);
  padding: 7rem 2rem 2rem 2rem;
  --invalid-msg-width: 50%;
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
  margin-top: 4rem;
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
</style>
