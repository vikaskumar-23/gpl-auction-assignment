// sessionStorage is per tab, so each tab keeps its own role across refreshes
const KEY = 'gpl.session'

export function loadSession() {
  try {
    return JSON.parse(sessionStorage.getItem(KEY))
  } catch {
    return null
  }
}

export function saveSession(session) {
  try {
    if (session) sessionStorage.setItem(KEY, JSON.stringify(session))
    else sessionStorage.removeItem(KEY)
  } catch {
    // storage blocked (private mode): role lasts until the page closes
  }
}
