<script setup lang="ts">
import { ref } from 'vue'
import Navbar from '../components/Nav-bar.vue'
import Map from '../components/Map.vue'

const activePanel = ref<'none' | 'search' | 'map'>('none')
const plateNumber = ref('')
const showColorPicker = ref(false)
const colorHoverLabel = ref('')
const mouseX = ref(0)
const mouseY = ref(0)
const colors = [
  { value: 'yellow', text: 'לוחית צהובה (רגילה)' },
  { value: 'red', text: 'לוחית אדומה (משטרה)' },
  { value: 'black', text: 'לוחית שחורה (צבא)' },
  { value: 'blue', text: 'לוחית כחולה (משטרה צבאית)' },
]
const selectedColor = ref(colors[0])

function togglePanels(panel: 'search' | 'map') {
  activePanel.value = panel
}

function controlSearchInput(event: Event) {
  const input = event.target as HTMLInputElement
  input.value = input.value.replace(/[^0-9]/g, '')

  switch (selectedColor.value?.value) {
    case 'yellow':
      input.maxLength = 8
      break
    case 'red':
    case 'black':
      input.maxLength = 7
      break
    case 'blue':
      input.maxLength = 3
      break
  }
}

function toggleColorPicker() {
  showColorPicker.value = !showColorPicker.value
}

function selectColor(color: any) {
  selectedColor.value = color
  toggleColorPicker()
  clearHoverLabel()
  plateNumber.value = ''
}

function setHoverLabel(label: any) {
  colorHoverLabel.value = label
}

function updateMousePosition(e: MouseEvent) {
  mouseX.value = e.clientX + 12
  mouseY.value = e.clientY + 12
}

function clearHoverLabel() {
  colorHoverLabel.value = ''
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
        <div v-if="activePanel === 'search'" class="panel panel-search">
          <div style="display: flex; gap: 10px; align-items: center">
            <input
              v-model="plateNumber"
              type="text"
              class="form-control"
              placeholder="הקלידו מספר רכב ללא קווים ואותיות"
              @input="controlSearchInput"
              style="width: 300px; height: 45px"
            />
            <div style="position: relative">
              <button
                type="button"
                @click="toggleColorPicker"
                @mousemove="updateMousePosition"
                @mouseover="setHoverLabel(selectedColor?.text)"
                @mouseleave="clearHoverLabel()"
                :style="{
                  backgroundColor: selectedColor?.value,
                  width: '45px',
                  height: '45px',
                  border: '3px solid #ccc',
                  borderRadius: '12px',
                  cursor: 'pointer',
                }"
              ></button>
              <div
                v-if="showColorPicker"
                style="
                  position: absolute;
                  right: 0;
                  background: whitesmoke;
                  border: 1px solid #ccc;
                  padding: 10px;
                  border-radius: 12px;
                  display: flex;
                  gap: 5px;
                  flex-wrap: wrap;
                  width: 160px;
                "
              >
                <button
                  v-for="color in colors"
                  :key="color.value"
                  type="button"
                  @click="selectColor(color)"
                  @mousemove="updateMousePosition"
                  @mouseover="setHoverLabel(color.text)"
                  @mouseleave="clearHoverLabel()"
                  :style="{
                    backgroundColor: color.value,
                    width: '30px',
                    height: '30px',
                    border: '1px solid #ccc',
                    borderRadius: '4px',
                    cursor: 'pointer',
                  }"
                ></button>
              </div>
              <div
                v-if="colorHoverLabel"
                :style="{
                  position: 'fixed',
                  left: mouseX + 'px',
                  top: mouseY + 'px',
                  background: 'whitesmoke',
                  color: 'black',
                  fontWeight: 'bold',
                  padding: '4px 8px',
                  borderRadius: '6px',
                  boxShadow: '0 1px 3px rgba(0,0,0,0.15)',
                  whiteSpace: 'nowrap',
                  pointerEvents: 'none',
                }"
              >
                {{ colorHoverLabel }}
              </div>
            </div>
          </div>
        </div>
        <div v-if="activePanel === 'map'" class="panel panel-map">
          <div
            id="map-placeholder"
            style="
              width: 100%;
              background: #f8f9fa;
              border: 1px dashed #ced4da;
              display: flex;
              align-items: center;
              justify-content: center;
            "
          >
            <Map />
          </div>
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
  max-width: 900px;
}

.home-view h1 {
  font-size: 5rem;
  margin-bottom: 0.5rem;
}

.home-view h1:last-of-type {
  margin-bottom: 5rem;
}

.home-actions {
  display: flex;
  gap: 3rem;
  justify-content: center;
  align-items: center;
  flex-wrap: wrap;
  margin-top: 1rem;
}

.home-panel {
  margin-top: 1.5rem;
  width: 100%;
  display: flex;
  justify-content: center;
}

.panel {
  max-width: 720px;
  width: 100%;
}

.panel-search .form-control {
  direction: ltr;
}

.panel-search {
  display: flex;
  justify-content: center;
}

input::placeholder {
  text-align: right;
}
</style>
