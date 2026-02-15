<script setup lang="ts">
import { onMounted, onBeforeUnmount, ref } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

interface Props {
  allowMarker?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  allowMarker: false,
})

let map: L.Map | null = null
let marker: L.Marker | null = null
const markerPosition = ref<[number, number] | null>(null)
const searchQuery = ref('')
const searchError = ref('')
const isSearching = ref(false)

async function searchAddress() {
  if (!searchQuery.value.trim()) return
  isSearching.value = true
  searchError.value = ''
  try {
    const url = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(searchQuery.value)}&countrycodes=IL&limit=1`
    const res = await fetch(url)
    const data = await res.json()
    if (data && data.length > 0) {
      const lat = parseFloat(data[0].lat)
      const lon = parseFloat(data[0].lon)
      map?.setView([lat, lon], 17)
    } else {
      searchError.value = 'אופס! לא רוצים לבאס אבל נראה שהמקום שהוזן לא נמצא, נסו לחפש ידנית.'
    }
  } catch (e) {
    searchError.value = 'אופס! נראה שיש שגיאה בחיפוש, קורה גם לטובים ביותר. נסו לחפש ידנית.'
  } finally {
    isSearching.value = false
  }
}

onMounted(() => {
  map = L.map('map', {
    center: [31.4853, 34.7818], // Israel
    zoom: 7,
  })

  const israelBounds = L.latLngBounds(
    [29.48, 34.2], // Southwest
    [33.35, 35.9], // Northeast
  )
  map.setMaxBounds(israelBounds)
  map.on('drag', function () {
    map!.panInsideBounds(israelBounds, { animate: false })
  })

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    minZoom: 7,
    attribution: '&copy; OpenStreetMap contributors',
  }).addTo(map)

  if (props.allowMarker) {
    map.on('click', (e: L.LeafletMouseEvent) => {
      if (marker) {
        marker.setLatLng(e.latlng)
      } else {
        marker = L.marker(e.latlng, { draggable: true }).addTo(map!)
        marker.on('dragend', () => {
          markerPosition.value = [marker!.getLatLng().lat, marker!.getLatLng().lng]
        })
      }
      markerPosition.value = [e.latlng.lat, e.latlng.lng]
    })
  }
})

onBeforeUnmount(() => {
  if (map) {
    map.remove()
    map = null
  }
  marker = null
})

defineExpose({ markerPosition })
</script>

<template>
  <form class="search-form" @submit.prevent="searchAddress">
    <input
      v-model="searchQuery"
      type="text"
      placeholder="כאן ניתן למצוא מהר כתובת או מקום בארץ"
      class="search-input"
      :disabled="isSearching"
    />
    <button type="submit" class="search-btn" :disabled="isSearching">
      <img src="../assets/icons/search.png" alt="search" />
    </button>
  </form>
  <div v-if="searchError" class="search-error">{{ searchError }}</div>
  <div id="map"></div>
</template>

<style scoped>
#map {
  height: 550px;
  width: 100%;
  border-radius: 8px;
}

.search-form {
  display: flex;
  flex-direction: row;
  gap: 1rem;
  margin-bottom: 1rem;
}

.search-input {
  flex: 1;
  height: 45px;
  padding: 0.5rem 1rem;
  font-size: 1.1rem;
}

.search-btn {
  padding: 0.5rem 1.2rem;
  background: cyan;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s;
}

.search-btn:hover {
  background-color: #00b7c7;
}

.search-btn:disabled {
  background: #aaa;
  cursor: not-allowed;
}

.search-btn img {
  height: 24px;
  width: 24px;
  vertical-align: middle;
}

.search-error {
  color: red;
  font-size: 1rem;
  margin-bottom: 0.5rem;
  text-align: right;
}
</style>
