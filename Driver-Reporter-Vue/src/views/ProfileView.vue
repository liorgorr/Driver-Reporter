<script setup lang="ts">
import Navbar from '../components/Nav-bar.vue'
import { ref, onMounted, watch } from 'vue'
import ReportBox from '../components/ReportBox.vue'
import { useAuth } from '../stores/auth'
import { getCsrfHeaders } from '../utils/csrf'
import { apiUrl } from '../utils/api'

const activePanel = ref<'none' | 'password' | 'reports'>('none')

const reportCount = ref(0)

interface Report {
  id: number
  plate_number: string
  offense_type: string
  date: string
  time: string
  description: string
  latitude_coordinate: number
  longitude_coordinate: number
}
const reports = ref<Report[]>([])

const password = ref('')
const confirmPassword = ref('')

const passwordValid = ref(true)
const confirmPasswordValid = ref(true)

const passwordError = ref('')
const confirmPasswordError = ref('')
const serverError = ref('')
const showSuccess = ref(false)

const showPassword = ref(false)
const showConfirmPassword = ref(false)

const isSubmitting = ref(false)
const hasAttemptedSubmit = ref(false)

const { isLoggedIn, username, syncAuthStatus } = useAuth()

function togglePanels(panel: 'password' | 'reports') {
  activePanel.value = panel
}

onMounted(async () => {
  await syncAuthStatus()

  if (!isLoggedIn.value) {
    return
  }

  try {
    const res = await fetch(apiUrl('/api/v1/reports/users/me/'), {
      credentials: 'include',
    })
    if (res.ok) {
      const data = await res.json()
      reportCount.value = data.count
      reports.value = data.reports
    }
  } catch (err) {
    if (err instanceof DOMException && err.name === 'AbortError') return
    console.error('Failed to fetch reports:', err)
  }
})

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

watch(password, (val) => {
  if (hasAttemptedSubmit.value) {
    passwordValid.value = validatePassword(val)
    if (confirmPassword.value) confirmPasswordValid.value = validateConfirm(confirmPassword.value)
  }
})

watch(confirmPassword, (val) => {
  if (hasAttemptedSubmit.value) confirmPasswordValid.value = validateConfirm(val)
})

async function handlePasswordChange() {
  await syncAuthStatus()

  if (!isLoggedIn.value) {
    return
  }

  hasAttemptedSubmit.value = true
  isSubmitting.value = true

  passwordValid.value = validatePassword(password.value)
  confirmPasswordValid.value = validateConfirm(confirmPassword.value)

  if (!passwordValid.value || !confirmPasswordValid.value) {
    setTimeout(() => {
      const firstInvalid = document.querySelector('.invalid-field, .invalid-msg')
      if (firstInvalid) firstInvalid.scrollIntoView({ behavior: 'smooth', block: 'center' })
    }, 50)
    isSubmitting.value = false
    return
  }

  serverError.value = ''

  try {
    const res = await fetch(apiUrl('/api/v1/auth/change-password/'), {
      method: 'PUT',
      credentials: 'include',
      headers: await getCsrfHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify({ password: password.value }),
    })

    if (res.ok) {
      showSuccess.value = true
      setTimeout(() => {
        window.location.href = window.location.pathname + window.location.search
      }, 2000)
    } else {
      const data = await res.json()
      serverError.value =
        'אופס! נראה שהשרת שלנו איבד את הדרך עם נסיון עדכון הסיסמא שלך 😕\nקורה גם לטובים ביותר 😉\nנסו שוב או חזרו מאוחר יותר'
      console.error('Password change error:', data)
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
    <section v-if="isLoggedIn" class="profile-view" dir="rtl">
      <h1>שלום {{ username }}</h1>
      <div class="profile-actions">
        <button
          type="button"
          class="btn btn-warning d-flex align-items-center gap-2"
          @click="togglePanels('reports')"
        >
          <img src="../assets/icons/licenceplate.png" width="30" height="30" />
          <span :class="{ 'fw-bold': activePanel === 'reports' }">הדיווחים שלי</span>
        </button>
        <button
          type="button"
          class="btn btn-info d-flex align-items-center gap-2"
          @click="togglePanels('password')"
        >
          <img src="../assets/icons/password.png" width="30" height="30" />
          <span :class="{ 'fw-bold': activePanel === 'password' }">שינוי סיסמה</span>
        </button>
      </div>

      <div v-if="activePanel === 'reports'" class="reports-panel">
        <div>
          <label v-if="reportCount > 0" class="search-results-label"
            >דיווחת כבר {{ reportCount }} דיווחים 🔥</label
          >
          <label v-if="reportCount === 0" class="no-results-label"
            >נראה שלא דיווחת (בינתיים 😉)</label
          >
        </div>

        <div v-if="reportCount > 0" class="report-list">
          <ReportBox
            v-for="report in reports"
            :reportId="report.id"
            :plateNumber="report.plate_number"
            :offenseType="report.offense_type"
            :date="report.date"
            :time="report.time"
            :description="report.description"
            :latitude="report.latitude_coordinate"
            :longitude="report.longitude_coordinate"
          />
        </div>
      </div>
      <div v-if="activePanel === 'password'" class="password-change-panel">
        <label for="password-change-password" class="password-change-label">סיסמא חדשה:</label>
        <div class="password-wrapper">
          <input
            id="password-change-password"
            v-model="password"
            :type="showPassword ? 'text' : 'password'"
            class="password-change-input"
            placeholder="לפחות 9 תווים הכוללים: מספר, אות קטנה ואות גדולה"
            :class="{ 'invalid-field': !passwordValid }"
            @keydown.enter="handlePasswordChange"
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

        <label for="password-change-password-confirmation" class="password-change-label"
          >אותה סיסמא חדשה פעם נוספת:</label
        >
        <div class="password-wrapper">
          <input
            id="password-change-password-confirmation"
            v-model="confirmPassword"
            :type="showConfirmPassword ? 'text' : 'password'"
            class="password-change-input"
            :class="{ 'invalid-field': !confirmPasswordValid }"
            @keydown.enter="handlePasswordChange"
            @paste.prevent
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
        <div v-if="showSuccess" class="success-message">הסיסמא שונתה בהצלחה!</div>
        <div v-if="serverError" class="error-message">{{ serverError }}</div>
        <button class="password-change-btn" @click="handlePasswordChange" :disabled="isSubmitting || showSuccess">
          <span>שינוי סיסמא</span>
        </button>
      </div>
    </section>
    <section v-else class="profile-view" dir="rtl">
      <h1>נראה שאינכם מחוברים 😵</h1>
    </section>
  </main>
</template>

<style scoped>
main {
  grid-column: 1 / -1;
  display: flex;
  justify-content: center;
}

.profile-view {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  gap: 1rem;
  padding: 7rem 2rem 2rem 2rem;
  min-width: 960px;
  width: 100%;
}

.profile-view h1 {
  font-size: 5rem;
  text-align: center;
  margin-bottom: 0.5rem;
  position: relative;
  z-index: 1;
  color: white;
}

.profile-view h1:first-of-type {
  margin-bottom: 3rem;
}

.profile-actions {
  display: flex;
  gap: 3rem;
  justify-content: center;
  align-items: center;
  flex-wrap: wrap;
  margin-top: 1rem;
  width: 100%;
}

.btn-warning:hover {
  background-color: #e0a800;
}

.btn-info:hover {
  background-color: #0bb8d8;
}

.search-results-label {
  display: block;
  color: white;
  font-size: 1.1rem;
  text-align: right;
  font-weight: bold;
  margin-top: 1.5rem;
}

.no-results-label {
  display: block;
  color: #d63333;
  font-size: 1.1rem;
  text-align: right;
  font-weight: bold;
  margin-top: 1.5rem;
}

.reports-panel {
  width: 100%;
  min-width: 96px;
  align-self: stretch;
}

.report-list {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 1.5rem;
  margin-top: 2rem;
  width: 100%;
  align-items: start;
  justify-items: stretch;
}

.password-change-panel {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  margin-top: 1.5rem;
  direction: rtl;
  width: 860px;
}

.password-wrapper {
  position: relative;
  width: 38%;
  margin-bottom: 1rem;
}

.password-wrapper .password-change-input {
  margin-bottom: 0;
  width: 100%;
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

.password-change-input {
  height: 45px;
  font-size: 1.1rem;
  padding: 0.5rem 1rem;
  margin-bottom: 1rem;
}

.password-change-input::placeholder {
  font-size: 0.85rem;
}

.password-change-label {
  font-size: 1.1rem;
  color: white;
  width: 38%;
  text-align: right;
}

.password-change-btn {
  background-color: #189359;
  color: #fff !important;
  border-radius: 6px;
  border-width: 0;
  padding: 0.3rem 0.6rem;
  transition: background 0.2s;
  margin-top: 2rem;
  width: 20%;
}

.password-change-btn:disabled {
  background: #aaa !important;
  color: #fff !important;
  cursor: not-allowed;
  opacity: 0.7;
}

.password-change-btn:hover {
  background-color: #157347;
}

.success-message {
  position: fixed;
  top: 80px;
  right: 0;
  left: 0;
  margin: 0 auto;
  z-index: 9999;
  width: fit-content;
  color: #189359;
  font-size: 1.3rem;
  font-weight: bold;
  background: #e6f9ed;
  border-radius: 6px;
  padding: 0.7rem 1.2rem;
  border: 1px solid #189359;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  text-align: center;
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

.invalid-field {
  border: 2px solid #d63333 !important;
}

.invalid-msg {
  color: #d63333;
  font-size: 1rem;
  margin-top: -0.7rem;
  text-align: right;
  width: 38%;
}
</style>
