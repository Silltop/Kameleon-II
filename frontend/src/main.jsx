import { render } from 'preact'
import './index.css'
import { App } from './app.jsx'
import { exchangeTokenForAPI } from './init/token-exchange'

// Initialize dark mode if stored
if (localStorage.theme === 'dark' || (!('theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
  document.documentElement.classList.add('dark')
} else {
  document.documentElement.classList.remove('dark')
}

// Exchange Keycloak session for API JWT token on app startup
exchangeTokenForAPI().catch(error => {
  console.error('Failed to initialize API authentication:', error)
  // Redirect to login if token exchange fails
  window.location.href = '/login'
})
