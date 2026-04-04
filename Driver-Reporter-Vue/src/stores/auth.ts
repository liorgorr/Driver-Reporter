import { ref } from 'vue'
import { apiUrl } from '../utils/api'

const isLoggedIn = ref<boolean>(false)
const username = ref<string>('')
let authSyncPromise: Promise<void> | null = null

function syncAuthStatus(): Promise<void> {
  if (authSyncPromise) {
    return authSyncPromise
  }

  authSyncPromise = (async () => {
    try {
      const res = await fetch(apiUrl('/api/v1/auth/status/'), {
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
      authSyncPromise = null
    }
  })()

  return authSyncPromise
}

export function useAuth() {
  return {
    isLoggedIn,
    username,
    syncAuthStatus,
  }
}
