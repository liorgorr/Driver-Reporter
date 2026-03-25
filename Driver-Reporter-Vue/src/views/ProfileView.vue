<script setup lang="ts">
import Navbar from '../components/Nav-bar.vue'
import { ref, onMounted } from 'vue'
import ReportBox from '../components/ReportBox.vue'
import { useAuth } from '../stores/auth'

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

const { isLoggedIn, username } = useAuth()

function togglePanels(panel: 'password' | 'reports') {
  activePanel.value = panel
}

onMounted(async () => {
  try {
    const res = await fetch(
      `http://localhost:8000/api/v1/reports/users/${encodeURIComponent(username.value)}/`,
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
})
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

      <div class="profile-panel">
        <div v-if="activePanel === 'reports'" class="reports-panel">
          <div>
            <label v-if="reportCount > 0" class="search-results-label"
              >דיווחת כבר {{reportCount}} דיווחים 🔥</label
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
        <div v-if="activePanel === 'password'"></div>
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
  max-width: 1400px;
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
  max-width: 860px;
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
  max-width: 1400px;
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
</style>
