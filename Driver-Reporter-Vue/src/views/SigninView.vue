<script setup lang="ts">
import { ref } from 'vue'
import Navbar from '../components/Nav-bar.vue'

const showPassword = ref(false)
</script>

<template>
  <main>
    <Navbar />
    <section class="signin-view" dir="rtl">
      <h1>כאן מתחברים לחשבון קיים.</h1>
      <div class="signin-content">
        <label for="signin-input" class="signin-label">שם משתשמש:</label>
        <input id="signin-input" type="text" class="signin-input" />
        <label for="signin-input" class="signin-label">סיסמא:</label>
        <div class="password-wrapper">
          <input
            id="signin-input"
            :type="showPassword ? 'text' : 'password'"
            class="signin-input"
          />
          <button type="button" class="eye-btn" @click="showPassword = !showPassword" tabindex="-1">
            <svg
              v-if="!showPassword"
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
              <circle cx="12" cy="12" r="3" />
            </svg>
            <svg
              v-else
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <path
                d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94"
              />
              <path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19" />
              <line x1="1" y1="1" x2="23" y2="23" />
            </svg>
          </button>
        </div>
        <button class="signin-btn">
          <span>כניסה</span>
        </button>
        <p class="signup-link">
          אין לך חשבון? <RouterLink to="/signup">כאן יוצרים אחד</RouterLink>
        </p>
      </div>
    </section>
  </main>
</template>

<style scoped>
main {
  grid-column: 1 / -1;
}

.signin-view {
  position: relative;
  width: 860px;
  min-height: calc(100vh - 7rem);
  color: #d63333;
  padding: 7rem 2rem 2rem 2rem;
}

.signin-view h1 {
  font-size: 5rem;
  text-align: center;
  margin-bottom: 0.5rem;
  position: relative;
  z-index: 1;
  color: white;
}

.signin-view h1:first-of-type {
  margin-bottom: 3rem;
}

.signin-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  direction: rtl;
}

.password-wrapper {
  position: relative;
  width: 55%;
  margin-bottom: 1rem;
}

.password-wrapper .signin-input {
  width: 100%;
  margin-bottom: 0;
  padding-left: 2.5rem;
  box-sizing: border-box;
}

.eye-btn {
  position: absolute;
  left: 0.6rem;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  cursor: pointer;
  padding: 0;
  color: #888;
  display: flex;
  align-items: center;
}

.eye-btn:hover {
  color: #333;
}

.eye-btn svg {
  width: 20px;
  height: 20px;
}

.signin-input {
  width: 55%;
  height: 45px;
  font-size: 1.1rem;
  padding: 0.5rem 1rem;
  margin-bottom: 1rem;
}

.signin-label {
  font-size: 1.1rem;
  color: white;
  width: 55%;
  text-align: right;
}

.signin-btn {
  background-color: #189359;
  color: #fff !important;
  border-radius: 6px;
  border-width: 0;
  padding: 0.3rem 0.6rem;
  transition: background 0.2s;
  margin-top: 2rem;
  width: 21%;
}

.signin-btn:hover {
  background-color: #157347;
}

.signup-link {
  color: #aaa;
  font-size: 0.9rem;
  margin-top: 0.5rem;
}

.signup-link a {
  color: #4f8ef7;
  text-decoration: none;
  font-weight: 600;
}

.signup-link a:hover {
  text-decoration: underline;
}
</style>
