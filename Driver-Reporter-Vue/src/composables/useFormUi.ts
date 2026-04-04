import type { Ref } from 'vue'

export function useFormUi() {
  function scrollToFirstInvalid(selector = '.invalid-field, .invalid-msg', delayMs = 50): void {
    setTimeout(() => {
      const firstInvalid = document.querySelector(selector)
      if (firstInvalid) {
        firstInvalid.scrollIntoView({ behavior: 'smooth', block: 'center' })
      }
    }, delayMs)
  }

  function showServerError(
    errorRef: Ref<string>,
    message: string,
    options: { durationMs?: number; scrollToTop?: boolean } = {},
  ): void {
    const { durationMs = 15000, scrollToTop = true } = options

    errorRef.value = message
    if (scrollToTop) {
      window.scrollTo({ top: 0, behavior: 'smooth' })
    }

    setTimeout(() => {
      errorRef.value = ''
    }, durationMs)
  }

  return {
    scrollToFirstInvalid,
    showServerError,
  }
}
