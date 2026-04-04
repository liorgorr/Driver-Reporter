<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import Navbar from '../components/Nav-bar.vue'
import PlateNumberInput from '../components/PlateNumberInput.vue'
import Map from '../components/Map.vue'
import { ref as vueRef } from 'vue'
import { useAuth } from '../stores/auth'
import { getCsrfHeaders } from '../utils/csrf'
import { apiUrl } from '../utils/api'
import { useFormUi } from '../composables/useFormUi'

const plateNumber = ref('')
const selectedOffenseType = ref('')
const ISRAEL_TIME_ZONE = 'Asia/Jerusalem'
const reportDate = ref('')
const reportTime = ref('')
const MAX_DESC = 300
const description = ref('')
const mapRef = vueRef()
const checked = ref(false)

const markerValid = ref(true)
const plateNumberValid = ref(true)
const offenseTypeValid = ref(true)
const dateValid = ref(true)
const descriptionValid = ref(true)
const checkedValid = ref(true)

const dateErrorMsg = ref('')
const markerErrorMsg = ref('')
const serverError = ref('')
const showSuccess = ref(false)
const isSubmitting = ref(false)
const hasAttemptedSubmit = ref(false)

const offenseTypes = ref([
  { value: 'red_light', text: 'רמזור אדום', icon: '🚦' },
  { value: 'phone', text: 'טלפון בנהיגה', icon: '📱' },
  { value: 'speeding', text: 'מהירות מסוכנת', icon: '🚗💨' },
  { value: 'bypassing', text: 'עקיפה מסוכנת', icon: '🚗↔️' },
  { value: 'crosswalk', text: 'זכות קדימה במעבר חציה', icon: '🚸' },
  { value: 'sidewalk_parking', text: 'חניה על מדרכה/מעבר חצייה', icon: '❌🅿️🚶' },
  { value: 'bike_lane_parking', text: 'חניה על שביל אופניים', icon: '❌🅿️🚴' },
  { value: 'other', text: 'אחר', icon: '💬' },
])

type DateTimeParts = {
  year: number
  month: number
  day: number
  hour: number
  minute: number
}

const israelDateTimeFormatter = new Intl.DateTimeFormat('en-GB', {
  timeZone: ISRAEL_TIME_ZONE,
  year: 'numeric',
  month: '2-digit',
  day: '2-digit',
  hour: '2-digit',
  minute: '2-digit',
  hour12: false,
})

const { isLoggedIn, syncAuthStatus } = useAuth()

onMounted(async () => {
  await syncAuthStatus()
})

async function validatePlateNumber(plateNumber: string) {
  const normalizedPlate = plateNumber.trim()

  if (!normalizedPlate) {
    return true
  }

  try {
    const res = await fetch(
      apiUrl(`/api/v1/reports/plates/${encodeURIComponent(normalizedPlate)}/`),
      {
        method: 'GET',
        credentials: 'include',
      },
    )

    if (!res.ok) {
      return true
    }

    const data = (await res.json()) as { reported_by_current_user?: boolean }
    return data.reported_by_current_user !== true
  } catch (err) {
    console.error('Plate validation failed:', err)
    return true
  }
}

function getNowInIsrael(): DateTimeParts {
  const parts = israelDateTimeFormatter.formatToParts(new Date())
  const readPart = (type: Intl.DateTimeFormatPartTypes): number => {
    const raw = parts.find((part) => part.type === type)?.value
    return raw ? Number(raw) : 0
  }

  return {
    year: readPart('year'),
    month: readPart('month'),
    day: readPart('day'),
    hour: readPart('hour'),
    minute: readPart('minute'),
  }
}

function getTodayInIsrael(): string {
  const now = getNowInIsrael()
  return `${now.year}-${String(now.month).padStart(2, '0')}-${String(now.day).padStart(2, '0')}`
}

const maxReportDate = ref(getTodayInIsrael())
const { scrollToFirstInvalid, showServerError } = useFormUi()

function getDaysInMonth(year: number, month: number): number {
  return new Date(year, month, 0).getDate()
}

function subtractOneMonth(dateTime: DateTimeParts): DateTimeParts {
  let year = dateTime.year
  let month = dateTime.month - 1
  if (month === 0) {
    month = 12
    year -= 1
  }

  const day = Math.min(dateTime.day, getDaysInMonth(year, month))
  return {
    year,
    month,
    day,
    hour: 0,
    minute: 0,
  }
}

function parseSelectedDateTime(date: string, time: string): DateTimeParts | null {
  const dateMatch = date.match(/^(\d{4})-(\d{2})-(\d{2})$/)
  if (!dateMatch) {
    return null
  }

  const year = Number(dateMatch[1])
  const month = Number(dateMatch[2])
  const day = Number(dateMatch[3])
  if (month < 1 || month > 12) {
    return null
  }

  if (day < 1 || day > getDaysInMonth(year, month)) {
    return null
  }

  let hour = 0
  let minute = 0
  if (time) {
    const timeMatch = time.match(/^(\d{2}):(\d{2})$/)
    if (!timeMatch) {
      return null
    }

    hour = Number(timeMatch[1])
    minute = Number(timeMatch[2])
    if (hour < 0 || hour > 23 || minute < 0 || minute > 59) {
      return null
    }
  }

  return { year, month, day, hour, minute }
}

function compareDateTime(left: DateTimeParts, right: DateTimeParts): number {
  if (left.year !== right.year) return left.year < right.year ? -1 : 1
  if (left.month !== right.month) return left.month < right.month ? -1 : 1
  if (left.day !== right.day) return left.day < right.day ? -1 : 1
  if (left.hour !== right.hour) return left.hour < right.hour ? -1 : 1
  if (left.minute !== right.minute) return left.minute < right.minute ? -1 : 1
  return 0
}

function validateDateTime(date: string, time: string) {
  const selectedDateTime = parseSelectedDateTime(date, time)

  if (!date || date.split('-').length !== 3 || !selectedDateTime) {
    dateErrorMsg.value = 'אופס! נראה שלא בחרת תאריך תקין'
    return false
  }

  const nowInIsrael = getNowInIsrael()

  if (compareDateTime(selectedDateTime, nowInIsrael) > 0) {
    dateErrorMsg.value = 'מזל טוב! נראה שבנית מכונת זמן כי הזמן או התאריך שבחרת עוד לא הגיעו'
    return false
  }

  const oneMonthAgo = subtractOneMonth(nowInIsrael)

  if (compareDateTime(selectedDateTime, oneMonthAgo) < 0) {
    dateErrorMsg.value = 'אופס! לא ניתן למלא דיווח על אירוע שקרה יותר מלפני חודש'
    return false
  }

  dateErrorMsg.value = ''
  return true
}

function validateMarker(markerPos: [number, number] | null) {
  if (
    !markerPos ||
    !Array.isArray(markerPos) ||
    markerPos.length !== 2 ||
    !markerPos[0] ||
    !markerPos[1]
  ) {
    markerErrorMsg.value = 'יש לסמן את מקום האירוע במפה'
    return false
  } else if (
    markerPos[0] < 29.49 ||
    markerPos[0] > 33.34 ||
    markerPos[1] < 34.266 ||
    markerPos[1] > 35.9
  ) {
    markerErrorMsg.value = 'אופס! נראה שהמיקום שסימנת לא נמצא בישראל'
    return false
  }
  return true
}

watch(plateNumber, async (newVal) => {
  plateNumberValid.value = await validatePlateNumber(newVal)
})

watch(selectedOffenseType, (newVal) => {
  if (hasAttemptedSubmit.value && newVal) {
    offenseTypeValid.value = true
  }
})

watch([reportDate, reportTime], ([newDate, newTime]) => {
  if (hasAttemptedSubmit.value) {
    dateValid.value = validateDateTime(newDate, newTime)
  }
})

watch([description, selectedOffenseType], ([newDesc, newOffense]) => {
  if (hasAttemptedSubmit.value) {
    if (newOffense === 'other') {
      descriptionValid.value = !!newDesc.trim()
    } else {
      descriptionValid.value = true
    }
  }
})

watch(checked, (newVal) => {
  if (hasAttemptedSubmit.value && newVal) {
    checkedValid.value = true
  } else if (hasAttemptedSubmit.value && !newVal) {
    checkedValid.value = false
  }
})

watch(
  () => mapRef.value?.markerPosition,
  (newPos) => {
    if (hasAttemptedSubmit.value) {
      markerValid.value = validateMarker(newPos as [number, number] | null)
    }
  },
)

async function handleSend() {
  hasAttemptedSubmit.value = true
  serverError.value = ''
  isSubmitting.value = true

  offenseTypeValid.value = !!selectedOffenseType.value
  dateValid.value = validateDateTime(reportDate.value, reportTime.value)

  if (selectedOffenseType.value === 'other') {
    descriptionValid.value = !!description.value.trim()
  } else {
    descriptionValid.value = true
  }
  const markerPos = mapRef.value?.markerPosition
  markerValid.value = validateMarker(markerPos as [number, number] | null)
  checkedValid.value = !!checked.value

  if (
    !plateNumberValid.value ||
    !offenseTypeValid.value ||
    !dateValid.value ||
    !descriptionValid.value ||
    !checkedValid.value ||
    !markerValid.value
  ) {
    scrollToFirstInvalid('.invalid-field, .invalid-msg, .invalid-plate-label')
    isSubmitting.value = false
    return
  }

  try {
    const payload = {
      plate_number: plateNumber.value,
      offense_type: (() => {
        const found = offenseTypes.value.find((o) => o.value === selectedOffenseType.value)
        return found ? `${found.icon} ${found.text}` : selectedOffenseType.value
      })(),
      date: reportDate.value,
      time: reportTime.value || null,
      description: description.value,
      latitude_coordinate: markerValid.value ? markerPos[0] : null,
      longitude_coordinate: markerValid.value ? markerPos[1] : null,
    }

    const res = await fetch(apiUrl('/api/v1/reports/create/'), {
      method: 'POST',
      credentials: 'include',
      headers: await getCsrfHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify(payload),
    })

    if (res.status === 201) {
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
          'אופס! נראה שהשרת שלנו איבד את הדרך עם הדיווח שלך 😕\nקורה גם לטובים ביותר 😉\nנסו שוב או חזרו מאוחר יותר',
        )
      }
      console.error('Report submission error:', data)
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
    <section v-if="isLoggedIn" class="report-view" dir="rtl">
      <h1>מדווחים. משפיעים.</h1>
      <PlateNumberInput @update:plateNumber="plateNumber = $event" />
      <label v-if="plateNumberValid" class="plate-label">* לא חובה, רק אם בטוחים במספר</label>
      <div v-if="!plateNumberValid" class="invalid-plate-label">
        אופס! נראה שכבר דיווחת על מספר זה
      </div>
      <select
        id="offense-type"
        v-model="selectedOffenseType"
        class="offense-dropdown"
        :class="{ 'invalid-field': !offenseTypeValid }"
      >
        <option value="" disabled selected hidden>בחרו את סוג העבירה</option>
        <option v-for="offense in offenseTypes" :key="offense.value" :value="offense.value">
          {{ offense.icon }} {{ offense.text
          }}{{ offense.value === 'other' ? ' (נא לפרט בתיאור)' : '' }}
        </option>
      </select>
      <div class="datetime-row">
        <div class="datetime-field">
          <label for="report-date">תאריך האירוע:</label>
          <input
            id="report-date"
            type="date"
            v-model="reportDate"
            :max="maxReportDate"
            :class="{ 'invalid-field': !dateValid }"
          />
        </div>
        <div class="datetime-field">
          <label for="report-time">שעת האירוע:</label>
          <input id="report-time" type="time" v-model="reportTime" />
        </div>
      </div>
      <div v-if="!dateValid && dateErrorMsg" class="invalid-msg date-error-msg">
        {{ dateErrorMsg }}
      </div>
      <div class="description-field">
        <textarea
          id="description"
          v-model="description"
          rows="4"
          :maxlength="MAX_DESC"
          placeholder="הוספת פירוט והערות... "
          :class="{ 'invalid-field': !descriptionValid }"
        ></textarea>
        <div
          class="char-counter"
          :class="{
            'char-counter--near': description.length >= MAX_DESC * 0.85,
            'char-counter--full': description.length === MAX_DESC,
          }"
        >
          {{ description.length }} / {{ MAX_DESC }}
        </div>
      </div>
      <div class="map-panel">
        <label for="map">סמנו את מקום האירוע בדיוק איפה שהוא קרה:</label>
        <Map :allowMarker="true" id="map" ref="mapRef" />
        <div v-if="!markerValid" class="invalid-msg">{{ markerErrorMsg }}</div>
      </div>
      <div class="checkbox-row">
        <span class="checkbox-wrapper" :class="{ 'invalid-field': !checkedValid }">
          <input type="checkbox" id="confirm-checkbox" v-model="checked" />
        </span>
        <label for="confirm-checkbox"
          >אני מצהיר/ה כי כל המידע שהזנתי נכון ומדויק וכי הייתי עד/ה לאירוע במו עיניי</label
        >
      </div>
      <button class="send-btn" @click="handleSend" :disabled="isSubmitting || showSuccess">
        <span>שליחת דיווח</span>
      </button>
      <div v-if="showSuccess" class="success-message">הדיווח נוסף בהצלחה!</div>
      <div v-if="serverError" class="error-message">{{ serverError }}</div>
    </section>
    <section v-else class="report-view" dir="rtl">
      <h1>מתחברים. מדווחים. משפיעים.</h1>
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

.report-view {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  color: #d63333;
  gap: 1rem;
  padding: 7rem 2rem 2rem 2rem;
  min-width: 960px;
  --invalid-msg-width: auto;
  --invalid-msg-margin-top: 0.5rem;
}

.report-view h1 {
  font-size: 5rem;
}

.report-view h1:first-of-type {
  margin-bottom: 3rem;
}

.plate-label {
  display: block;
  color: white;
  font-size: 1.1rem;
  text-align: right;
  width: 355px;
  margin-top: -0.7rem;
}

.invalid-plate-label {
  display: block;
  color: #d63333;
  font-size: 1rem;
  text-align: right;
  width: 355px;
  margin-top: -0.7rem;
}

.offense-dropdown {
  margin-top: 1rem;
  width: 355px;
  height: 45px;
  padding: 0.5rem;
}

.datetime-row {
  display: flex;
  gap: 2rem;
  margin-top: 1rem;
}

.datetime-field {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.25rem;
}

.datetime-field label {
  font-size: 1.1rem;
  color: white;
}

.datetime-field input[type='date'],
.datetime-field input[type='time'] {
  width: 160px;
  padding: 0.5rem;
}

.description-field {
  margin-top: 1rem;
  width: 355px;
}

.description-field textarea {
  width: 100%;
  min-height: 70px;
  padding: 0.75rem;
}

.char-counter {
  text-align: left;
  font-size: 0.78rem;
  color: #666;
  margin-top: 0.2rem;
  transition: color 0.2s;
}

.char-counter--near {
  color: #e0a800;
}

.char-counter--full {
  color: #d63333;
  font-weight: 600;
}

.map-panel {
  margin-top: 1rem;
  width: 450px;
}

.map-panel label {
  font-size: 1.1rem;
  color: white;
  margin-bottom: 0.2rem;
  align-self: flex-end;
  text-align: right;
  width: 100%;
}

.checkbox-row {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  width: 100%;
  gap: 0.5rem;
  margin-top: 1rem;
}

.checkbox-row label {
  font-size: 1.1rem;
  color: white;
}

.send-btn {
  background-color: #189359;
  color: #fff !important;
  border-radius: 6px;
  border-width: 0;
  padding: 0.3rem 0.6rem;
  transition: background 0.2s;
  width: 20%;
}

.send-btn:hover {
  background-color: #157347;
}

.send-btn:disabled {
  background: #aaa !important;
  color: #fff !important;
  cursor: not-allowed;
  opacity: 0.7;
}

.checkbox-wrapper {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 18px;
  height: 18px;
  border-radius: 3px;
}

.checkbox-wrapper input[type='checkbox'] {
  margin: 0;
  width: 18px;
  height: 18px;
  vertical-align: middle;
}

.date-error-msg {
  margin-top: -0.5rem;
}
</style>
