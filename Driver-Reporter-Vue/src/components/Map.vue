<script setup lang="ts">
import { onMounted, onBeforeUnmount } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

let map: L.Map | null = null

onMounted(() => {
  map = L.map('map', {
    center: [31.4853, 34.7818],
    zoom: 7,
  })

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; OpenStreetMap contributors',
  }).addTo(map)
})

onBeforeUnmount(() => {
  if (map) {
    map.remove()
    map = null
  }
})
</script>

<template>
  <div id="map"></div>
</template>

<style scoped>
#map {
  height: 550px;
  width: 100%;
  border-radius: 8px;
}
</style>
