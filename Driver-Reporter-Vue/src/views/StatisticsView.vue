<script setup lang="ts">
import { ref, onMounted } from 'vue'
import Navbar from '../components/Nav-bar.vue'

const distinctPlateCount = ref<number>(0)
const reportCount = ref<number>(0)
const maxReportedPlate = ref<number>(0)
const maxReportedPrefix = ref<string>('')
const maxReportedCount = ref<number>(0)

function animateCount(target: number, parameter: { value: any }, duration = 2000) {
  const start = performance.now()
  const step = (now: number) => {
    const progress = Math.min((now - start) / duration, 1)
    const eased = 1 - Math.pow(1 - progress, 3)
    parameter.value = Math.round(eased * target)
    if (progress < 1) requestAnimationFrame(step)
  }
  requestAnimationFrame(step)
}

onMounted(async () => {
  try {
    var response = await fetch('http://localhost:8000/api/v1/reports/distinct-plate-count/')
    if (response.ok) {
      const data = await response.json()
      animateCount(data.count, distinctPlateCount)
    }
  } catch (err) {
    console.error('Failed to fetch distinct plate count:', err)
  }
  try {
    response = await fetch('http://localhost:8000/api/v1/reports/count/')
    if (response.ok) {
      const data = await response.json()
      animateCount(data.count, reportCount)
    }
  } catch (err) {
    console.error('Failed to fetch report count:', err)
  }
  try {
    response = await fetch('http://localhost:8000/api/v1/reports/max-reported-plate/')
    if (response.ok) {
      const data = await response.json()
      const raw: string = data.maxReported['plate_number']
      const parts = raw.split(' - ')
      const digits = parts.length > 1 ? parts[1] : parts[0]
      maxReportedPrefix.value = parts.length > 1 ? parts[0] + ' - ' : ''
      animateCount(Number(digits), maxReportedPlate)
      animateCount(data.maxReported['count'], maxReportedCount)
    }
  } catch (err) {
    console.error('Failed to fetch max reported plate:', err)
  }
})
</script>

<template>
  <main>
    <Navbar />
    <section class="statistics-view" dir="rtl">
      <h1>כאן משנים מציאות.</h1>
      <h3 class="stat-1">{{ distinctPlateCount }} מספרי רכב כבר דווחו</h3>
      <h3 class="stat-2">
        הרכב הכי מדווח הוא {{ maxReportedPrefix }}{{ maxReportedPlate }} <br /><span class="stat-2-sub"
          >עם {{ maxReportedCount }} דיווחים</span
        >
      </h3>
      <h3 class="stat-3">סוג הדיווח הכי נפוץ הוא רמזור אדום עם 0 דיווחים</h3>
      <h3 class="stat-4">{{ reportCount }} דיווחים התקבלו בסך הכל</h3>
    </section>
  </main>
</template>

<style scoped>
main {
  grid-column: 1 / -1;
}

.statistics-view {
  position: relative;
  width: 100%;
  min-height: calc(100vh - 7rem);
  color: #d63333;
  padding: 7rem 2rem 2rem 2rem;
}

.statistics-view h1 {
  font-size: 5rem;
  text-align: center;
  margin-bottom: 0.5rem;
  position: relative;
  z-index: 1;
  color: green;
}

.statistics-view h3 {
  text-align: right;
  position: absolute;
  white-space: nowrap;
}

.statistics-view h1:first-of-type {
  margin-bottom: 3rem;
}

.stat-1 {
  top: 35%;
  left: -70%;
  transform: rotate(-15deg);
  font-size: 2.5rem;
  font-family: Georgia, 'Times New Roman', Times, serif;
  color: orange;
}

.stat-2 {
  top: 55%;
  left: 100%;
  transform: rotate(35deg);
  font-size: 1.2rem;
}

.stat-2-sub {
  display: block;
  text-align: center;
}

.stat-3 {
  top: 60%;
  left: 20%;
  transform: rotate(180deg);
  font-size: 1rem;
  font-family: 'Courier New', Courier, monospace;
}

.stat-4 {
  top: 70%;
  right: 70%;
  transform: rotate(45deg);
  font-size: 2rem;
}
</style>
