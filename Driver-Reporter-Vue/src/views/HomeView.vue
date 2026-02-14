<script setup lang="ts">
import { ref } from 'vue'
import Navbar from '../components/Nav-bar.vue'
import Map from '../components/Map.vue'
import PlateNumberInput from '../components/PlateNumberInput.vue'

const activePanel = ref<'none' | 'search' | 'map'>('none')
const plateNumber = ref('')
const selectedColor = ref({ value: 'yellow', text: 'לוחית צהובה (רגילה)' })

function togglePanels(panel: 'search' | 'map') {
  activePanel.value = panel
}
</script>

<template>
  <main>
    <Navbar />
    <section class="home-view" dir="rtl">
      <h1>
        0 <br />
        רכבים כבר דווחו
      </h1>
      <div class="home-actions">
        <button
          type="button"
          class="btn btn-warning d-flex align-items-center gap-2"
          :class="{ active: activePanel === 'search' }"
          @click="togglePanels('search')"
        >
          <img src="../assets/icons/licenceplate.png" width="30" height="30" alt="licence plate" />
          <span :class="{ 'fw-bold': activePanel === 'search' }">חיפוש לפי מספר רכב</span>
        </button>
        <button
          type="button"
          class="btn btn-info d-flex align-items-center gap-2"
          :class="{ active: activePanel === 'map' }"
          @click="togglePanels('map')"
        >
          <img src="../assets/icons/map.png" width="30" height="30" alt="map" />
          <span :class="{ 'fw-bold': activePanel === 'map' }">צפייה במפה</span>
        </button>
      </div>

      <div class="home-panel">
        <div v-if="activePanel === 'search'">
          <PlateNumberInput
            v-model:plateNumber="plateNumber"
            v-model:selectedColor="selectedColor"
          />
        </div>
        <div v-if="activePanel === 'map'" class="map-panel">
          <Map />
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
  max-width: 720px;
}

.home-view h1 {
  font-size: 5rem;
  margin-bottom: 0.5rem;
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

.map-panel {
  width: 450px;
}
</style>
