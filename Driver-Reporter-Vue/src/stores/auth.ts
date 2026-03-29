import { ref } from 'vue'

const isLoggedIn = ref<boolean>(false)
const username = ref<string>('')
const isSyncingAuth = ref<boolean>(false)

async function syncAuthStatus() {
  if (isSyncingAuth.value) {
    return
  }

  isSyncingAuth.value = true

  try {
    const res = await fetch('http://localhost:8000/api/v1/auth/status/', {
      credentials: 'include',
    })

    if (!res.ok) {
      isLoggedIn.value = false
      username.value = ''
      return
    }

    const data = (await res.json()) as { authenticated?: boolean; username?: string }
    isLoggedIn.value = data.authenticated === true
    username.value = data.authenticated === true ? (data.username ?? '') : ''
  } catch (err) {
    console.error('Auth status sync failed:', err)
    isLoggedIn.value = false
    username.value = ''
  } finally {
    isSyncingAuth.value = false
  }
}

export function useAuth() {
  return {
    isLoggedIn,
    username,
    syncAuthStatus,
  }
}
