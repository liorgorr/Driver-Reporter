<script setup lang="ts">
import { computed, ref, onMounted, watch } from 'vue'
import Navbar from '../components/Nav-bar.vue'
import Map from '../components/Map.vue'
import type { MapMarker } from '../components/Map.vue'
import PlateNumberInput from '../components/PlateNumberInput.vue'
import ReportBox from '../components/ReportBox.vue'
import { apiUrl } from '../utils/api'

const activePanel = ref<'none' | 'search' | 'map'>('none')
const distinctPlateCount = ref<number>(0)

function animateCount(target: number, duration = 2000) {
  const start = performance.now()
  const step = (now: number) => {
    const progress = Math.min((now - start) / duration, 1)
    const eased = 1 - Math.pow(1 - progress, 3)
    distinctPlateCount.value = Math.round(eased * target)
    if (progress < 1) requestAnimationFrame(step)
  }
  requestAnimationFrame(step)
}

onMounted(async () => {
  try {
    const res = await fetch(apiUrl('/api/v1/reports/distinct-plate-count/'))
    if (res.ok) {
      const data = await res.json()
      animateCount(data.count)
    }
  } catch (err) {
    console.error('Failed to fetch distinct plate count:', err)
  }
})

const plateNumber = ref('')
const plateInputRef = ref<InstanceType<typeof PlateNumberInput> | null>(null)
const defaultColor = { value: 'yellow', text: 'לוחית צהובה (רגילה)' }
const selectedColor = ref(defaultColor)
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

let searchDebounceTimer: ReturnType<typeof setTimeout> | null = null
let searchAbortController: AbortController | null = null

watch(plateNumber, (newVal) => {
  if (searchDebounceTimer) clearTimeout(searchDebounceTimer)
  if (searchAbortController) searchAbortController.abort()

  if (!newVal) {
    reportCount.value = 0
    reports.value = []
    return
  }

  searchDebounceTimer = setTimeout(async () => {
    searchAbortController = new AbortController()
    const { signal } = searchAbortController

    try {
      const res = await fetch(
        apiUrl(`/api/v1/reports/plates/${encodeURIComponent(newVal)}/`),
        { signal },
      )
      if (res.ok) {
        const data = await res.json()
        reportCount.value = data.count
        reports.value = data.reports
      }
    } catch (err) {
      if (err instanceof DOMException && err.name === 'AbortError') return
      console.error('Failed to fetch reports:', err)
    }
  }, 10)
})

const platePreviewStyle = computed(() => {
  const color = selectedColor.value.value
  const isDark = color === 'black' || color === 'blue' || color === 'red'

  return {
    backgroundColor: color,
    borderColor: isDark ? 'white' : '#1a1a1a',
    color: isDark ? 'white' : 'black',
    boxShadow: '0 10px 24px rgba(0, 0, 0, 0.12)',
  }
})

const allReports = ref<MapMarker[]>([])
const dateFrom = ref('')
const dateTo = ref('')

const filteredReports = computed(() => {
  if (!dateFrom.value && !dateTo.value) return allReports.value
  return allReports.value.filter((r) => {
    if (dateFrom.value && r.date < dateFrom.value) return false
    if (dateTo.value && r.date > dateTo.value) return false
    return true
  })
})

async function fetchAllReports() {
  if (allReports.value.length > 0) return
  try {
    const res = await fetch(apiUrl('/api/v1/reports/all/'))
    if (res.ok) {
      const data = await res.json()
      allReports.value = data.reports.map((r: Report) => ({
        id: r.id,
        lat: r.latitude_coordinate,
        lng: r.longitude_coordinate,
        plateNumber: r.plate_number,
        offenseType: r.offense_type,
        description: r.description,
        date: r.date,
        time: r.time,
      }))
    }
  } catch (err) {
    console.error('Failed to fetch all reports:', err)
  }
}

function togglePanels(panel: 'search' | 'map') {
  if (panel === 'search') {
    plateNumber.value = ''
    reportCount.value = 0
    reports.value = []
    selectedColor.value = defaultColor
    plateInputRef.value?.reset()
  }
  activePanel.value = panel
}

onMounted(() => {
  fetchAllReports()
})
</script>

<template>
  <main>
    <Navbar />
    <section class="home-view" dir="rtl">
      <h1>
        {{ distinctPlateCount }} <br />
        רכבים כבר דווחו
      </h1>
      <div class="home-actions">
        <button
          type="button"
          class="btn btn-warning d-flex align-items-center gap-2"
          @click="togglePanels('search')"
        >
          <img src="../assets/icons/licenceplate.png" width="30" height="30" />
          <span :class="{ 'fw-bold': activePanel === 'search' }">חיפוש לפי מספר רכב</span>
        </button>
        <button
          type="button"
          class="btn btn-info d-flex align-items-center gap-2"
          @click="togglePanels('map')"
        >
          <img src="../assets/icons/map.png" width="30" height="30" />
          <span :class="{ 'fw-bold': activePanel === 'map' }">צפייה במפה</span>
        </button>
      </div>

      <div class="home-panel">
        <div v-if="activePanel === 'search'" class="search-panel">
          <div class="search-controls">
            <PlateNumberInput
              ref="plateInputRef"
              @update:plateNumber="plateNumber = $event"
              @update:selectedColor="selectedColor = $event"
            />
            <label v-if="plateNumber && reportCount > 0" class="search-results-label"
              >{{ reportCount }} דיווחים נמצאו עבור המספר:</label
            >
            <label v-if="plateNumber && reportCount === 0" class="no-results-label"
              >לא נמצאו דיווחים עבור המספר הזה (בינתיים 😉)</label
            >
            <div
              v-if="plateNumber && reportCount > 0"
              class="plate-preview"
              :style="platePreviewStyle"
            >
              <span class="plate-preview-text">{{ plateNumber }}</span>
            </div>
          </div>

          <div v-if="plateNumber && reportCount > 0" class="report-list">
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
              :plateColor="selectedColor.value"
            />
          </div>
        </div>
        <div v-if="activePanel === 'map'" class="map-panel">
          <div class="date-filter" dir="rtl">
            <div class="date-filter-row">
              <label>מתאריך:</label>
              <input type="date" v-model="dateFrom" class="date-input" />
              <label>עד תאריך:</label>
              <input type="date" v-model="dateTo" class="date-input" />
            </div>
            <div class="date-filter-row">
              <button
                v-if="dateFrom || dateTo"
                class="clear-dates-btn"
                @click="((dateFrom = ''), (dateTo = ''))"
              >
                ניקוי הסינון
              </button>
              <span class="filter-count" v-if="dateFrom || dateTo">
                מציג {{ filteredReports.length }} מתוך {{ allReports.length }} דיווחים
              </span>
            </div>
          </div>
          <Map :markers="filteredReports" />
        </div>
      </div>
    </section>
  </main>
</template>

<style scoped>
main {
  grid-column: 1 / -1;
  display: flex;
  justify-content: center;
}

.home-view {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  color: #d63333;
  gap: 1rem;
  padding: 7rem 2rem 2rem 2rem;
  min-width: 960px;
  width: 100%;
}

.home-view h1 {
  font-size: 5rem;
  margin-bottom: 0.5rem;
  max-width: 720px;
}

.home-view h1:first-of-type {
  margin-bottom: 3rem;
}

.home-actions {
  display: flex;
  gap: 3rem;
  justify-content: center;
  align-items: center;
  flex-wrap: wrap;
  margin-top: 1rem;
  max-width: 720px;
}

.btn-warning:hover {
  background-color: #e0a800;
}

.btn-info:hover {
  background-color: #0bb8d8;
}

.home-panel {
  margin-top: 1.5rem;
  width: 100%;
  display: flex;
  justify-content: center;
}

.search-results-label {
  display: block;
  color: white;
  font-size: 1.1rem;
  text-align: right;
  font-weight: bold;
  margin-top: 0.5rem;
}

.no-results-label {
  display: block;
  color: #d63333;
  font-size: 1.1rem;
  text-align: right;
  font-weight: bold;
  margin-top: 0.5rem;
}

.plate-preview {
  margin-top: 1.25rem;
  width: 100%;
  height: 70px;
  border: 4px solid #1a1a1a;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  letter-spacing: 0.35rem;
  margin-top: 2rem;
}

.plate-preview::before,
.plate-preview::after {
  content: '';
  position: absolute;
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.28);
  top: 50%;
  transform: translateY(-50%);
}

.plate-preview::before {
  left: 14px;
}

.plate-preview::after {
  right: 14px;
}

.plate-preview-text {
  font-size: 2rem;
  font-weight: 700;
}

.map-panel {
  width: 450px;
}

.date-filter {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.4rem;
}

.date-filter-row {
  margin-bottom: 1rem;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.6rem;
  justify-content: right;
  width: 100%;
  text-align: right;
}

.date-filter label {
  font-size: 0.95rem;
  color: #ccc;
  white-space: nowrap;
}

.date-input {
  padding: 0.35rem 0.7rem;
  border-radius: 6px;
  border: 1px solid #555;
  background: #1a1a1a;
  color: #fff;
  font-size: 0.95rem;
  cursor: pointer;
}

.date-input::-webkit-calendar-picker-indicator {
  filter: invert(1);
  cursor: pointer;
}

.clear-dates-btn {
  padding: 0.35rem 0.9rem;
  border-radius: 6px;
  border: none;
  background: #d63333;
  color: #fff;
  font-size: 0.9rem;
  cursor: pointer;
  transition: background 0.2s;
}

.clear-dates-btn:hover {
  background: #b02020;
}

.filter-count {
  font-size: 0.85rem;
  color: #aaa;
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

.search-panel {
  width: 100%;
  max-width: 1400px;
}

.search-controls {
  max-width: 355px;
  width: 100%;
  margin: 0 auto;
}
</style>
