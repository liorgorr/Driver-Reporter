<script setup lang="ts">
import { useRoute } from 'vue-router'

const route = useRoute()
</script>

<template>
  <main>
    <section class="not-found-view" dir="rtl">
      <h1>נראה שגילית חור שחור 😵</h1>
      <router-link to="/" class="back-home">
        <img src="../assets/icons/favicon.png" width="30" height="30" />
        כאן אפשר לחזור הביתה
      </router-link>
    </section>
  </main>
</template>

<style scoped>
main {
  grid-column: 1 / -1;
  display: flex;
  justify-content: center;
}

.not-found-view {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  position: relative;
  width: 880px;
  padding: 7rem 2rem 2rem 2rem;
}

.not-found-view h1 {
  font-size: 5rem;
  text-align: center;
  margin-bottom: 0.5rem;
  position: relative;
  color: white;
}

.not-found-view h1:first-of-type {
  margin-bottom: 3rem;
}

.back-home {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  width: fit-content;
  margin-inline: auto;
  padding: 0.8rem 1.3rem;
  border-radius: 0.65rem;
  font-size: 1.1rem;
  font-weight: 600;
  text-decoration: none;
  background: #0f172a;
  color: #fff;
  transition:
    background-color 0.2s ease,
    transform 0.2s ease;
}

.back-home:hover,
.back-home:focus-visible {
  background: #1f2937;
  transform: translateY(-1px);
}
</style>
