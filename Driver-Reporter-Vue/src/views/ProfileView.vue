<script setup lang="ts">
import Navbar from '../components/Nav-bar.vue'
import { ref, onMounted, watch } from 'vue'
import ReportBox from '../components/ReportBox.vue'
import PasswordField from '../components/PasswordField.vue'
import { useAuth } from '../stores/auth'
import { getCsrfHeaders } from '../utils/csrf'
import { apiUrl } from '../utils/api'
import { usePasswordValidation } from '../composables/usePasswordValidation'
import { useFormUi } from '../composables/useFormUi'

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

const isSubmitting = ref(false)
const hasAttemptedSubmit = ref(false)

const { isLoggedIn, username, syncAuthStatus } = useAuth()
const { validatePassword, validateConfirmPassword } = usePasswordValidation(
  username,
  password,
  passwordError,
  confirmPasswordError,
)
const { scrollToFirstInvalid, showServerError } = useFormUi()

function togglePanels(panel: 'password' | 'reports') {
  activePanel.value = panel
}

onMounted(async () => {
  await syncAuthStatus()

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

async function handlePasswordChange() {
  hasAttemptedSubmit.value = true
  isSubmitting.value = true

  passwordValid.value = validatePassword(password.value)
  confirmPasswordValid.value = validateConfirmPassword(confirmPassword.value)

  if (!passwordValid.value || !confirmPasswordValid.value) {
    scrollToFirstInvalid()
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
      if (res.status === 401) {
        showServerError(serverError, 'אופס! נראה שאינך מחובר/ת 😕')
      } else {
        showServerError(
          serverError,
          'אופס! נראה שהשרת שלנו איבד את הדרך עם נסיון עדכון הסיסמא שלך 😕\nקורה גם לטובים ביותר 😉\nנסו שוב או חזרו מאוחר יותר',
        )
      }
      console.error('Password change error:', data)
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
        <PasswordField
          id="password-change-password"
          v-model="password"
          placeholder="לפחות 9 תווים הכוללים: מספר, אות קטנה ואות גדולה"
          :invalid="!passwordValid"
          width="38%"
          placeholderFontSize="0.85rem"
          @enter="handlePasswordChange"
        />
        <div v-if="!passwordValid" class="invalid-msg">{{ passwordError }}</div>

        <label for="password-change-password-confirmation" class="password-change-label"
          >אותה סיסמא חדשה פעם נוספת:</label
        >
        <PasswordField
          id="password-change-password-confirmation"
          v-model="confirmPassword"
          :invalid="!confirmPasswordValid"
          :preventPaste="true"
          width="38%"
          @enter="handlePasswordChange"
        />
        <div v-if="!confirmPasswordValid" class="invalid-msg">{{ confirmPasswordError }}</div>
        <div v-if="showSuccess" class="success-message">הסיסמא שונתה בהצלחה!</div>
        <div v-if="serverError" class="error-message">{{ serverError }}</div>
        <button
          class="password-change-btn"
          @click="handlePasswordChange"
          :disabled="isSubmitting || showSuccess"
        >
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
@import '../assets/form-feedback.css';

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
  --invalid-msg-width: 38%;
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

</style>
