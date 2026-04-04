import type { Ref } from 'vue'

type PasswordValidationMessages = {
  required: string
  minLength: string
  needNumber: string
  needLower: string
  needUpper: string
  containsUsername: string
  confirmRequired: string
  confirmMismatch: string
}

const defaultMessages: PasswordValidationMessages = {
  required: 'זה אולי לא קל אבל חייבים לבחור סיסמא 😉',
  minLength: 'הסיסמא חייבת להכיל לפחות 9 תווים 😕',
  needNumber: 'הסיסמא חייבת להכיל לפחות מספר אחד 😕',
  needLower: 'הסיסמא חייבת להכיל לפחות אות אחת קטנה באנגלית 😕',
  needUpper: 'הסיסמא חייבת להכיל לפחות אות אחת גדולה באנגלית 😕',
  containsUsername: 'אופס! הסיסמא לא יכולה להכיל את שם המשתמש 😕 גם אנחנו שונאים האקרים 😉',
  confirmRequired: 'זה אולי קצת מציק אבל חייבים לאשר את הסיסמא 😉',
  confirmMismatch: 'אופס! נראה שהסיסמאות לא תואמות 😕 אולי כדאי לבדוק שוב? 😉',
}

export function usePasswordValidation(
  username: Ref<string>,
  password: Ref<string>,
  passwordError: Ref<string>,
  confirmPasswordError: Ref<string>,
  messages: PasswordValidationMessages = defaultMessages,
) {
  function validatePassword(value: string): boolean {
    if (!value) {
      passwordError.value = messages.required
      return false
    }

    if (value.length < 9) {
      passwordError.value = messages.minLength
      return false
    }

    if (!/[0-9]/.test(value)) {
      passwordError.value = messages.needNumber
      return false
    }

    if (!/[a-z]/.test(value)) {
      passwordError.value = messages.needLower
      return false
    }

    if (!/[A-Z]/.test(value)) {
      passwordError.value = messages.needUpper
      return false
    }

    if (value.includes(username.value)) {
      passwordError.value = messages.containsUsername
      return false
    }

    passwordError.value = ''
    return true
  }

  function validateConfirmPassword(value: string): boolean {
    if (!value && password.value) {
      confirmPasswordError.value = messages.confirmRequired
      return false
    }

    if (value !== password.value) {
      confirmPasswordError.value = messages.confirmMismatch
      return false
    }

    confirmPasswordError.value = ''
    return true
  }

  return {
    validatePassword,
    validateConfirmPassword,
  }
}
