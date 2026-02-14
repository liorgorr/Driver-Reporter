<script setup lang="ts">
import Navbar from '../components/Nav-bar.vue'
</script>

<template>
  <main>
    <Navbar />
    <section class="about-view" dir="rtl">
      <h1>תרבות נהיגה חדשה מתחילה כאן.</h1>
      <p>
        מלשינהג מאפשר לך לדווח על נהגים מסוכנים בכביש, ולתרום לשיפור הבטיחות בדרכים באמצעות יצירת
        הרתעה ומיפוי של אזורים מסוכנים. <br />
        <br />התחברו לאתר ודווחו על נהיגה מסוכנת תחת החלונית "דיווח חדש". בנוסף לכך, תוכלו לראות
        בעמוד הראשי דיווחים של משתמשים קודמים לפי מספר רכב או לפי מיקומים במפה.
      </p>
      <h3>הצטרפו עוד היום למהפכה והצילו חיים!</h3>
    </section>
  </main>
</template>

<style scoped>
main {
  grid-column: 1 / -1;
  display: flex;
  justify-content: center;
}

.about-view {
  display: flex;
  flex-direction: column;
  color: #d63333;
  gap: 1rem;
  padding: 7rem 2rem 2rem 2rem;
  max-width: 1200px;
}

.about-view h1 {
  font-size: 5rem;
  text-align: center;
  margin-bottom: 0.5rem;
}

.about-view h3 {
  font-size: 3rem;
  text-align: center;
}

.about-view h1:first-of-type {
  margin-bottom: 3rem;
}

.about-view p {
  font-size: 1.5rem;
  text-align: right;
}

.about-view p:last-of-type {
  margin-bottom: 3rem;
}
</style>
