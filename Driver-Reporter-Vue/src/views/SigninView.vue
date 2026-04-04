<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import Navbar from '../components/Nav-bar.vue'
import PasswordField from '../components/PasswordField.vue'
import { useAuth } from '../stores/auth'
import { getCsrfHeaders } from '../utils/csrf'
import { apiUrl } from '../utils/api'
import { useFormUi } from '../composables/useFormUi'

const router = useRouter()

const username = ref('')
const password = ref('')

const usernameValid = ref(true)
const passwordValid = ref(true)

const usernameError = ref('')
const passwordError = ref('')
const wrongInputError = ref('')
const serverError = ref('')

const isSubmitting = ref(false)
const hasAttemptedSubmit = ref(false)

const { isLoggedIn, syncAuthStatus } = useAuth()
const { scrollToFirstInvalid, showServerError } = useFormUi()

onMounted(async () => {
  await syncAuthStatus()
})

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

watch(username, (val) => {
  if (hasAttemptedSubmit.value) usernameValid.value = validateUsername(val)
  wrongInputError.value = ''
})

watch(password, (val) => {
  if (hasAttemptedSubmit.value) passwordValid.value = validatePassword(val)
  wrongInputError.value = ''
})

async function handleSignin() {
  await syncAuthStatus()

  if (isLoggedIn.value) {
    return
  }

  hasAttemptedSubmit.value = true
  isSubmitting.value = true

  usernameValid.value = validateUsername(username.value)
  passwordValid.value = validatePassword(password.value)

  if (!usernameValid.value || !passwordValid.value) {
    scrollToFirstInvalid()
    isSubmitting.value = false
    return
  }

  wrongInputError.value = ''
  serverError.value = ''

  try {
    const res = await fetch(apiUrl('/api/v1/auth/login/'), {
      method: 'POST',
      credentials: 'include',
      headers: await getCsrfHeaders({ 'Content-Type': 'application/json' }),
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
      } else if (res.status === 429) {
        wrongInputError.value = 'אופס! נראה שלא הצלחת להתחבר יותר מידי פעמים, נסו שוב בעוד דקה 😕'
      } else {
        const data = await res.json()
        showServerError(
          serverError,
          'אופס! נראה שהשרת שלנו איבד את הדרך עם נסיון ההתחברות שלך 😕\nקורה גם לטובים ביותר 😉\nנסו שוב או חזרו מאוחר יותר',
        )
        console.error('Signin error:', data)
      }
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
        <PasswordField
          id="signin-password"
          v-model="password"
          :invalid="!passwordValid"
          @enter="handleSignin"
        />
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
    <section v-else class="signin-view" dir="rtl">
      <h1>נראה שאתם כבר מחוברים 😎</h1>
    </section>
  </main>
</template>

<style scoped>
@import '../assets/form-feedback.css';

main {
  grid-column: 1 / -1;
}

.signin-view {
  position: relative;
  min-width: 960px;
  min-height: calc(100vh - 7rem);
  padding: 7rem 2rem 2rem 2rem;
  --invalid-msg-width: 50%;
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
  margin-top: 4rem;
}

.signin-input {
  width: 50%;
  height: 45px;
  font-size: 1.1rem;
  padding: 0.5rem 1rem;
  margin-bottom: 1rem;
}

.signin-label {
  font-size: 1.1rem;
  color: white;
  width: 50%;
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
  width: 20%;
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
