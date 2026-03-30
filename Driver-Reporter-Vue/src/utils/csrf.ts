import { apiUrl } from './api'

const CSRF_COOKIE_NAME = 'csrftoken'

let csrfInitPromise: Promise<void> | null = null

function getCookie(name: string): string | null {
  const value = `; ${document.cookie}`
  const parts = value.split(`; ${name}=`)
  if (parts.length === 2) {
    return parts.pop()?.split(';').shift() ?? null
  }
  return null
}

export async function ensureCsrfCookie(): Promise<void> {
  if (getCookie(CSRF_COOKIE_NAME)) {
    return
  }

  if (!csrfInitPromise) {
    csrfInitPromise = fetch(apiUrl('/api/v1/auth/csrf/'), {
      method: 'GET',
      credentials: 'include',
    })
      .then(() => undefined)
      .finally(() => {
        csrfInitPromise = null
      })
  }

  await csrfInitPromise
}

export async function getCsrfHeaders(baseHeaders: HeadersInit = {}): Promise<Headers> {
  await ensureCsrfCookie()

  const headers = new Headers(baseHeaders)
  const token = getCookie(CSRF_COOKIE_NAME)

  if (token) {
    headers.set('X-CSRFToken', token)
  }

  return headers
}
