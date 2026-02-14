<script setup lang="ts">
import Navbar from '../components/Nav-bar.vue'
</script>

<template>
  <main>
    <Navbar />
    <section class="statistics-view" dir="rtl">
      <h1>כאן משנים מציאות.</h1>
      <h3 class="stat-1">0 מספרי רכב כבר דווחו</h3>
      <h3 class="stat-2">שיא הדיווחים על אותו רכב הוא 0</h3>
      <h3 class="stat-3">סוג הדיווח הכי נפוץ הוא רמזור אדום עם 0 דיווחים</h3>
      <h3 class="stat-4">0 דיווחים התקבלו בסך הכל</h3>
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

.stat-3 {
  top: 60%;
  left: 30%;
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
