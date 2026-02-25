<script setup lang="ts">
import { computed, ref } from 'vue'

const props = defineProps<{
  reportId?: number
  plateNumber?: string
  offenseType?: string
  time?: string
  date?: string
  description?: string
  latitude?: number | null
  longitude?: number | null
  plateColor?: string
}>()

const plateBadgeStyle = computed(() => {
  const color = props.plateColor
  const isDark = color === 'black' || color === 'blue' || color === 'red'

  return {
    backgroundColor: color,
    border: `2px solid ${isDark ? 'white' : '#1a1a1a'}`,
    color: isDark ? 'white' : 'black',
    boxShadow: '0 10px 24px rgba(0, 0, 0, 0.12)',
  }
})

function copyCoords() {
  if (props.latitude == null || props.longitude == null) return
  navigator.clipboard.writeText(`${props.latitude.toFixed(5)}, ${props.longitude.toFixed(5)}`)
}
</script>

<template>
  <div class="report-box" dir="rtl">
    <div class="report-box__header">
      <span class="plate-badge" :style="plateBadgeStyle">{{ plateNumber || '—' }}</span>
      <span class="offense-label">{{ offenseType || '—' }}</span>
      <span v-if="reportId != null" class="report-id">#{{ reportId }}</span>
    </div>

    <div class="report-box__body">
      <div class="field">
        <span class="field__icon">📅</span>
        <span class="field__label">תאריך</span>
        <span class="field__value">{{ date || '—' }}</span>
      </div>

      <div class="field">
        <span class="field__icon">🕐</span>
        <span class="field__label">שעה</span>
        <span class="field__value">{{ time ? time.slice(0, 5) : 'לא צוינה' }}</span>
      </div>

      <div class="field field--full">
        <span class="field__icon">📝</span>
        <span class="field__label">תיאור</span>
        <span class="field__value field__value--desc">{{ description || 'לא צוין' }}</span>
      </div>

      <div class="field field--coords">
        <span class="field__icon">📍</span>
        <span class="field__label">קואורדינטות לחיפוש במפה</span>
        <span class="field__value coords-value">
          <template v-if="latitude != null && longitude != null">
            {{ latitude.toFixed(5) }}, {{ longitude.toFixed(5) }}
            <button class="copy-btn" @click="copyCoords" :title="'העתקה'">
              {{ '📋' }}
            </button>
          </template>
          <template v-else>—</template>
        </span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.report-box {
  background: #111;
  border: 1px solid #2a2a2a;
  border-radius: 12px;
  overflow: hidden;
  width: 100%;
  height: 555px;
  font-family: 'Assistant', sans-serif;
  color: #e0e0e0;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.6);
}

.report-box__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  background: #1a1a1a;
  padding: 0.85rem 1.1rem;
  border-bottom: 1px solid #2a2a2a;
  flex-wrap: wrap;
}

.plate-badge {
  font-size: 1.25rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  padding: 0.25rem 0.8rem;
  border-radius: 6px;
  white-space: nowrap;
  direction: ltr;
}

.offense-label {
  font-size: 0.95rem;
  color: #d63333;
  font-weight: 600;
  flex: 1;
}

.report-id {
  font-size: 0.75rem;
  color: #555;
  font-weight: 500;
  white-space: nowrap;
}

.report-box__body {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0;
}

.field {
  display: flex;
  flex-direction: column;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #1e1e1e;
  border-left: 1px solid #1e1e1e;
  gap: 0.15rem;
}

.field:nth-child(odd) {
  border-left: none;
}

.field--full {
  grid-column: 1 / -1;
  border-left: none;
}

.field--coords {
  grid-column: 1 / -1;
  border-left: none;
  align-items: center;
  text-align: center;
}

.field__icon {
  font-size: 1rem;
  line-height: 1;
}

.field__label {
  font-size: 0.7rem;
  color: #666;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.field__value {
  font-size: 0.95rem;
  color: #e0e0e0;
  font-weight: 500;
}

.field__value--desc {
  white-space: pre-wrap;
  word-break: break-word;
  font-weight: 400;
  color: #bbb;
}

.coords-value {
  font-size: 0.85rem;
  direction: ltr;
  text-align: center;
  color: #88b8ff;
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.copy-btn {
  background: none;
  border: none;
  padding: 0;
  cursor: pointer;
  font-size: 0.9rem;
  line-height: 1;
  opacity: 0.7;
  transition:
    opacity 0.15s,
    transform 0.15s;
  user-select: none;
}

.copy-btn:hover {
  opacity: 1;
  transform: scale(1.2);
}
</style>
