<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useAuth } from '../stores/auth'
import { getCsrfHeaders } from '../utils/csrf'
import { apiUrl } from '../utils/api'

const { isLoggedIn, syncAuthStatus } = useAuth()
const router = useRouter()

async function handleSignout() {
  try {
    await fetch(apiUrl('/api/v1/auth/logout/'), {
      method: 'POST',
      credentials: 'include',
      headers: await getCsrfHeaders(),
    })
    await syncAuthStatus()
  } catch (err) {
    console.error('Signout request failed:', err)
  } finally {
    await router.push('/')
  }
}
</script>

<template>
  <nav class="navbar fixed-top navbar-expand-lg navbar-custom" data-bs-theme="dark" dir="rtl">
    <div class="container-fluid justify-content-start">
      <router-link to="/" class="navbar-brand" active-class="fw-bold">
        <img src="../assets/icons/favicon.png" width="30" height="30" />
        מלשינהג
      </router-link>
      <router-link to="/about" class="navbar-brand" active-class="fw-bold">
        <img src="../assets/icons/about.png" width="30" height="30" />
        אודות
      </router-link>
      <router-link to="/statistics" class="navbar-brand" active-class="fw-bold">
        <img src="../assets/icons/statistics.png" width="25" height="25" />
        נתונים
      </router-link>
      <router-link to="/report" class="navbar-brand report-box" active-class="fw-bold">
        <img src="../assets/icons/plus.png" width="20" height="20" />
        דיווח חדש
      </router-link>
      <router-link v-if="isLoggedIn" to="/profile" class="navbar-brand" active-class="fw-bold">
        <img src="../assets/icons/profile.png" width="30" height="30" />
        פרופיל
      </router-link>
      <button v-if="isLoggedIn" class="navbar-brand" @click="handleSignout">
        <img src="../assets/icons/signout.png" width="23" height="23" />
        התנתקות
      </button>
      <router-link v-if="!isLoggedIn" to="/signin" class="navbar-brand" active-class="fw-bold">
        כניסה
      </router-link>
      <router-link
        v-if="!isLoggedIn"
        to="/signup"
        class="navbar-brand signup-box"
        active-class="fw-bold"
      >
        הרשמה
      </router-link>
    </div>
  </nav>
</template>

<style scoped>
.navbar {
  border-radius: 0;
}

.container-fluid {
  gap: 0.5rem;
}

.navbar-custom {
  --bs-navbar-bg: #0f172a;
  background-color: var(--bs-navbar-bg) !important;
}

.navbar-brand {
  font-size: 20px;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  margin-right: -0.4rem;
}

.navbar-brand:hover {
  background-color: #ffffff14;
  border-radius: 6px;
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

.signup-box {
  background-color: transparent;
  color: #fff !important;
  border: 1px solid #fff;
  border-radius: 6px;
  padding: 0.3rem 0.6rem;
  margin-inline: 0.25rem;
}

button.navbar-brand {
  background: none;
  border: none;
}
</style>
