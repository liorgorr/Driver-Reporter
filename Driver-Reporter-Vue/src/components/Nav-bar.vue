<script setup lang="ts"></script>

<template>
  <nav class="navbar fixed-top navbar-expand-lg bg-body-tertiary" data-bs-theme="dark" dir="rtl">
    <div class="container-fluid justify-content-start">
      <router-link to="/" class="navbar-brand" active-class="fw-bold">
        <img src="../assets/icons/favicon.png" width="30" height="30" alt="driver" />
        מלשינהג
      </router-link>
      <router-link to="/about" class="navbar-brand" active-class="fw-bold">
        <img src="../assets/icons/about.png" width="30" height="30" alt="about" />
        אודות
      </router-link>
      <router-link to="/statistics" class="navbar-brand" active-class="fw-bold">
        <img src="../assets/icons/statistics.png" width="25" height="25" alt="statistics" />
        נתונים
      </router-link>
      <router-link to="/report" class="navbar-brand report-box" active-class="fw-bold">
        <img src="../assets/icons/plus.png" width="20" height="20" alt="statistics" />
        דיווח חדש
      </router-link>
    </div>
  </nav>
</template>

<style scoped>
.navbar {
  border-radius: 0;
}

.navbar-brand {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  margin-right: -0.4rem;
}

.navbar-brand:hover {
  background-color: gray;
  border-radius: 6px;
  text-decoration: none;
}

.navbar-brand img {
  display: inline-block;
}

.report-box {
  background-color: #189359;
  color: #fff !important;
  border-radius: 6px;
  padding: 0.3rem 0.6rem;
  margin-inline: 0.25rem;
  margin-inline-start: auto;
}

.navbar-brand.report-box:hover {
  background-color: #157347;
  text-decoration: none;
}
</style>
