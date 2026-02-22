<script setup lang="ts">
import { ref, watch } from 'vue'
import Navbar from '../components/Nav-bar.vue'
import PlateNumberInput from '../components/PlateNumberInput.vue'
import Map from '../components/Map.vue'
import { onMounted, ref as vueRef } from 'vue'

const plateNumber = ref('')
const selectedColor = ref({ value: 'yellow', text: 'לוחית צהובה (רגילה)' })

const offenseTypes = ref([
  { value: 'red_light', text: 'רמזור אדום', icon: '🚦' },
  { value: 'phone', text: 'טלפון בנהיגה', icon: '📱' },
  { value: 'speeding', text: 'מהירות מסוכנת', icon: '🚗💨' },
  { value: 'bypassing', text: 'עקיפה מסוכנת', icon: '🚗↔️' },
  { value: 'crosswalk', text: 'זכות קדימה במעבר חציה', icon: '🚸' },
  { value: 'sidewalk_parking', text: 'חניה על מדרכה/מעבר חצייה', icon: '❌🅿️🚶' },
  { value: 'bike_lane_parking', text: 'חניה על שביל אופניים', icon: '❌🅿️🚴' },
  { value: 'other', text: 'אחר (נא לפרט בתיאור)', icon: '💬' },
])

const selectedOffenseType = ref('')
const reportDate = ref('')
const reportTime = ref('')
const description = ref('')
const checked = ref(false)

const mapRef = vueRef()
const markerValid = ref(true)
const offenseTypeValid = ref(true)
const dateValid = ref(true)
const descriptionValid = ref(true)
const checkedValid = ref(true)
const dateErrorMsg = ref('')

const showSuccess = ref(false)
const isLoading = ref(false)
const hasAttemptedSubmit = ref(false)

function validateDateTime(date: string, time: string) {
  if (!date || date.split('-').length !== 3) {
    return false
  }

  let selectedDateTime: Date
  if (time) {
    selectedDateTime = new Date(`${date}T${time}`)
  } else {
    selectedDateTime = new Date(`${date}T00:00:00`)
  }

  const now = new Date()
  const oneMonthAgo = new Date()
  oneMonthAgo.setMonth(now.getMonth() - 1)

  if (selectedDateTime > now) {
    dateErrorMsg.value = 'מזל טוב! נראה שבנית מכונת זמן כי הזמן או התאריך שבחרת עוד לא הגיעו'
    return false
  }

  if (selectedDateTime < oneMonthAgo) {
    dateErrorMsg.value = 'אופס! לא ניתן למלא דיווח על אירוע שקרה יותר מלפני חודש'
    return false
  }

  dateErrorMsg.value = ''
  return true
}

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
    if (
      hasAttemptedSubmit.value &&
      newPos &&
      Array.isArray(newPos) &&
      newPos.length === 2 &&
      newPos[0] &&
      newPos[1]
    ) {
      markerValid.value = true
    }
  },
  { deep: true },
)

const submitError = ref('')

async function handleSend() {
  hasAttemptedSubmit.value = true
  submitError.value = ''
  isLoading.value = true

  offenseTypeValid.value = !!selectedOffenseType.value
  dateValid.value = validateDateTime(reportDate.value, reportTime.value)

  if (selectedOffenseType.value === 'other') {
    descriptionValid.value = !!description.value.trim()
  } else {
    descriptionValid.value = true
  }
  checkedValid.value = !!checked.value
  let markerPos = mapRef.value?.markerPosition
  markerValid.value =
    markerPos && Array.isArray(markerPos) && markerPos.length === 2 && markerPos[0] && markerPos[1]

  if (
    offenseTypeValid.value &&
    dateValid.value &&
    descriptionValid.value &&
    checkedValid.value &&
    markerValid.value
  ) {
    try {
      const payload = {
        user_name: 'lior', // Placeholder until we implement user accounts
        plate_number: plateNumber.value,
        offense_type_name:
          offenseTypes.value.find((o) => o.value === selectedOffenseType.value)?.text ??
          selectedOffenseType.value,
        date: reportDate.value,
        time: reportTime.value || null,
        description: description.value,
        latitude_coordinate: markerPos[0],
        longitude_coordinate: markerPos[1],
      }

      const response = await fetch('http://localhost:8000/api/v1/reports/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })

      if (response.status === 201) {
        showSuccess.value = true
        setTimeout(() => {
          window.location.href = window.location.pathname + window.location.search
        }, 2000)
      } else {
        const data = await response.json()
        submitError.value =
          'אופס! נראה שהשרת שלנו איבד את הדרך עם הדיווח שלך 😕\nקורה גם לטובים ביותר 😉\nנסו שוב או חזרו מאוחר יותר'
        console.error('Report submission error:', data)
        window.scrollTo({ top: 0, behavior: 'smooth' })
        setTimeout(() => {
          submitError.value = ''
        }, 15000)
      }
      isLoading.value = false
    } catch (err) {
      submitError.value =
        'אופס! נראה שהשרת שלנו יצא לשנ"צ 😴\nגם הטובים ביותר צריכים לנוח 😉\nנסו שוב או חזרו מאוחר יותר'
      console.error('Network error:', err)
      window.scrollTo({ top: 0, behavior: 'smooth' })
      setTimeout(() => {
        submitError.value = ''
      }, 15000)
      isLoading.value = false
    }
  } else {
    setTimeout(() => {
      const firstInvalid = document.querySelector('.invalid-field, .invalid-msg')
      if (firstInvalid) {
        firstInvalid.scrollIntoView({ behavior: 'smooth', block: 'center' })
      }
    }, 50)
    isLoading.value = false
  }
}
</script>

<template>
  <main>
    <Navbar />
    <section class="report-view" dir="rtl">
      <h1>מדווחים. משפיעים.</h1>
      <PlateNumberInput v-model:plateNumber="plateNumber" v-model:selectedColor="selectedColor" />
      <label class="plate-label">* לא חובה, רק אם אתם בטוחים במספר</label>
      <select
        id="offense-type"
        v-model="selectedOffenseType"
        class="offense-dropdown"
        :class="{ 'invalid-field': !offenseTypeValid }"
      >
        <option value="" disabled selected hidden>בחרו את סוג העבירה</option>
        <option v-for="offense in offenseTypes" :key="offense.value" :value="offense.value">
          {{ offense.icon }} {{ offense.text }}
        </option>
      </select>
      <div class="datetime-row">
        <div class="datetime-field">
          <label for="report-date">תאריך האירוע:</label>
          <input
            id="report-date"
            type="date"
            v-model="reportDate"
            :max="new Date().toISOString().split('T')[0]"
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
          placeholder="הוספת פירוט והערות... "
          :class="{ 'invalid-field': !descriptionValid }"
        ></textarea>
      </div>
      <div class="map-panel">
        <label for="report-time">סמנו את מקום האירוע בדיוק איפה שהוא קרה:</label>
        <Map :allowMarker="true" ref="mapRef" />
        <div v-if="!markerValid" class="invalid-msg">יש לסמן את מקום האירוע במפה</div>
      </div>
      <div class="checkbox-row">
        <span class="checkbox-wrapper" :class="{ 'invalid-field': !checkedValid }">
          <input type="checkbox" id="confirm-checkbox" v-model="checked" />
        </span>
        <label for="confirm-checkbox"
          >אני מצהיר/ה כי כל המידע שהזנתי נכון ומדויק וכי הייתי עד/ה לאירוע במו עיניי</label
        >
      </div>
      <button
        class="send-btn"
        @click="handleSend"
        :disabled="isLoading || showSuccess"
      >
        <span>שליחת דיווח</span>
      </button>
      <div v-if="showSuccess" class="success-message">הדיווח נוסף בהצלחה!</div>
      <div v-if="submitError" class="error-message">{{ submitError }}</div>
    </section>
  </main>
</template>

<style scoped>
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
  max-width: 720px;
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
  justify-content: flex-start;
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

.invalid-msg {
  color: #d63333;
  font-size: 1rem;
  margin-top: 0.5rem;
  text-align: right;
}

.date-error-msg {
  margin-top: -0.5rem;
}
</style>
