<script setup lang="ts">
import { onMounted, onBeforeUnmount, ref, watch } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

export interface MapMarker {
  id: number
  lat: number
  lng: number
  plateNumber?: string
  offenseType: string
  description?: string
  date: string
  time?: string
}

interface Props {
  allowMarker?: boolean
  markers?: MapMarker[]
}

const props = withDefaults(defineProps<Props>(), {
  allowMarker: false,
  markers: () => [],
})

let map: L.Map | null = null
let marker: L.Marker | null = null
const displayMarkers: L.Marker[] = []
const markerPosition = ref<[number, number] | null>(null)
const searchQuery = ref('')
const searchError = ref('')
const isSearching = ref(false)

function offenseColor(offenseType: string): string {
  const t = offenseType
  if (t.includes('חניה')) return '#1976d2'
  if (t.includes('אחר')) return '#888888'
  return '#d63333'
}

function createPopupContent(m: MapMarker): HTMLDivElement {
  const container = document.createElement('div')
  container.style.fontFamily = 'Assistant, sans-serif'
  container.style.minWidth = '140px'
  container.style.textAlign = 'right'

  const idLine = document.createElement('span')
  idLine.style.display = 'block'
  idLine.style.direction = 'ltr'
  idLine.style.textAlign = 'left'
  idLine.textContent = `#${m.id}`
  container.appendChild(idLine)

  const plateLine = document.createElement('div')
  const plateValue = document.createElement('strong')
  plateValue.textContent = m.plateNumber || 'לא צוין מספר רכב'
  plateLine.appendChild(plateValue)

  if (m.plateNumber) {
    const copyBtn = document.createElement('button')
    copyBtn.type = 'button'
    copyBtn.title = 'העתקה'
    copyBtn.textContent = '📋'
    copyBtn.style.marginRight = '6px'
    copyBtn.style.background = 'none'
    copyBtn.style.border = 'none'
    copyBtn.style.cursor = 'pointer'
    copyBtn.style.fontSize = '0.85rem'
    copyBtn.style.opacity = '0.7'
    copyBtn.style.verticalAlign = 'middle'
    copyBtn.style.padding = '0'
    copyBtn.addEventListener('mouseenter', () => {
      copyBtn.style.opacity = '1'
    })
    copyBtn.addEventListener('mouseleave', () => {
      copyBtn.style.opacity = '0.7'
    })
    copyBtn.addEventListener('click', () => {
      const digitsOnly = m.plateNumber?.replace(/[^\d]/g, '') ?? ''
      if (!digitsOnly || !navigator.clipboard) {
        return
      }
      void navigator.clipboard.writeText(digitsOnly)
    })
    plateLine.appendChild(copyBtn)
  }

  container.appendChild(plateLine)

  const offenseLine = document.createElement('span')
  offenseLine.textContent = m.offenseType
  container.appendChild(offenseLine)
  container.appendChild(document.createElement('br'))

  const dateLine = document.createElement('strong')
  dateLine.textContent = `תאריך: ${m.date ? m.date.split('-').reverse().join('-') : 'לא צוין'}`
  container.appendChild(dateLine)
  container.appendChild(document.createElement('br'))

  const timeLine = document.createElement('strong')
  timeLine.textContent = `שעה: ${m.time ? m.time.slice(0, 5) : 'לא צוינה שעה'}`
  container.appendChild(timeLine)
  container.appendChild(document.createElement('br'))

  const descriptionLine = document.createElement('span')
  descriptionLine.style.fontSize = '0.85em'
  descriptionLine.style.color = '#555'
  descriptionLine.style.wordBreak = 'break-word'
  const descriptionLabel = document.createElement('strong')
  descriptionLabel.textContent = 'תיאור: '
  descriptionLine.appendChild(descriptionLabel)
  descriptionLine.appendChild(document.createTextNode(m.description || 'לא צוין תיאור'))
  container.appendChild(descriptionLine)

  return container
}

function renderMarkers(markers: MapMarker[]) {
  if (!map) return
  markers.forEach((m) => {
    const color = offenseColor(m.offenseType)
    const icon = L.divIcon({
      className: '',
      html: `<div style="width:12px;height:12px;border-radius:50%;background:${color};border:2px solid #fff;box-shadow:0 0 4px rgba(0,0,0,0.6)"></div>`,
      iconSize: [12, 12],
      iconAnchor: [6, 6],
    })
    const lm = L.marker([m.lat, m.lng], { icon }).addTo(map!).bindPopup(createPopupContent(m))
    displayMarkers.push(lm)
  })
}

async function searchAddress() {
  if (!searchQuery.value.trim()) return
  isSearching.value = true
  searchError.value = ''

  const coordMatch = searchQuery.value.trim().match(/^(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)$/)
  if (coordMatch) {
    const lat = parseFloat(coordMatch[1]!)
    const lng = parseFloat(coordMatch[2]!)
    map?.setView([lat, lng], 19)

    const matched = displayMarkers.find((dm) => {
      const ll = dm.getLatLng()
      return Math.abs(ll.lat - lat) < 0.000001 && Math.abs(ll.lng - lng) < 0.000001
    })
    if (matched) {
      matched.openPopup()
      const el = matched.getElement()?.querySelector('div') as HTMLElement | null
      if (el) {
        el.style.transition = 'none'
        el.style.outline = '3px solid #fff'
        el.style.outlineOffset = '3px'
        el.style.transform = 'scale(2)'
        setTimeout(() => {
          el.style.transition = 'transform 0.4s ease, outline 0.4s ease, outline-offset 0.4s ease'
          el.style.transform = 'scale(1)'
          el.style.outline = 'none'
          el.style.outlineOffset = '0px'
        }, 1000)
      }
    }

    isSearching.value = false
    return
  }

  try {
    const url = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(searchQuery.value)}&countrycodes=IL&limit=1`
    const res = await fetch(url)
    const data = await res.json()
    if (data && data.length > 0) {
      const lat = parseFloat(data[0].lat)
      const lon = parseFloat(data[0].lon)
      map?.setView([lat, lon], 19)
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

  if (props.markers && props.markers.length > 0) {
    renderMarkers(props.markers)
  }
})

watch(
  () => props.markers,
  (newMarkers) => {
    displayMarkers.forEach((m) => m.remove())
    displayMarkers.length = 0
    if (newMarkers) {
      renderMarkers(newMarkers)
    }
  },
)

onBeforeUnmount(() => {
  displayMarkers.forEach((m) => m.remove())
  displayMarkers.length = 0

  if (marker) {
    marker.off()
    marker.remove()
    marker = null
  }

  if (map) {
    map.off()
    map.remove()
    map = null
  }
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
