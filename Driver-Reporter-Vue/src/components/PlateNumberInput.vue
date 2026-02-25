<script setup lang="ts">
import { ref, watch } from 'vue'

const emit = defineEmits(['update:plateNumber', 'update:selectedColor'])

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

const localPlate = ref('')
const defaultColor = { value: 'yellow', text: 'לוחית צהובה (רגילה)' }
const localSelectedColor = ref(defaultColor)

function plateWithSuffix(digits: string, colorValue: string): string {
  if (!digits) return ''

  switch (colorValue) {
    case 'red':
      return 'מ - ' + digits
    case 'black':
      return 'צ - ' + digits
    case 'blue':
      return 'מצ - ' + digits
    default:
      return digits
  }
}

watch(localPlate, (v) =>
  emit('update:plateNumber', plateWithSuffix(v, localSelectedColor.value.value)),
)
watch(localSelectedColor, (v) => {
  emit('update:selectedColor', v)
})

function handlePlateNumberInput(event: Event) {
  const input = event.target as HTMLInputElement
  input.value = input.value.replace(/[^0-9]/g, '')

  switch (localSelectedColor.value.value) {
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

  localPlate.value = input.value
}

function toggleColorPicker() {
  showColorPicker.value = !showColorPicker.value
}

function selectColor(color: any) {
  localSelectedColor.value = color
  toggleColorPicker()
  clearHoverLabel()
  localPlate.value = ''
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

function reset() {
  localPlate.value = ''
  localSelectedColor.value = defaultColor
  showColorPicker.value = false
}

defineExpose({ reset })
</script>

<template>
  <div class="plate-search">
    <input
      v-model="localPlate"
      type="text"
      class="plate-search-input"
      placeholder="הקלידו מספר רכב ללא קווים ואותיות"
      @input="handlePlateNumberInput"
    />
    <div style="position: relative">
      <button
        type="button"
        class="color-button"
        @click="toggleColorPicker"
        @mousemove="updateMousePosition"
        @mouseover="setHoverLabel(localSelectedColor.text)"
        @mouseleave="clearHoverLabel()"
        :style="{
          backgroundColor: localSelectedColor.value,
        }"
      ></button>
      <div v-if="showColorPicker" class="color-picker">
        <button
          v-for="color in colors"
          :key="color.value"
          type="button"
          class="color-library-button"
          @click="selectColor(color)"
          @mousemove="updateMousePosition"
          @mouseover="setHoverLabel(color.text)"
          @mouseleave="clearHoverLabel()"
          :style="{
            backgroundColor: color.value,
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
</template>

<style scoped>
.plate-search {
  display: flex;
  justify-content: center;
  display: flex;
  gap: 1rem;
  align-items: center;
  direction: rtl;
}

.plate-search-input {
  width: 293px;
  height: 45px;
  font-size: 1.1rem;
  padding: 0.5rem 1rem;
  direction: ltr;
}

input::placeholder {
  text-align: right;
}

.color-button {
  width: 45px;
  height: 45px;
  border: 3px solid #ccc;
  border-radius: 12px;
  cursor: pointer;
}

.color-picker {
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
}

.color-library-button {
  width: 30px;
  height: 30px;
  border: 1px solid #ccc;
  border-radius: 4px;
  cursor: pointer;
}
</style>
