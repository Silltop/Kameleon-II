import { h, render } from 'preact'
import { ToastManager } from '../components/ToastManager'
import { initializeToastSystem } from '../utils/_toast'

/**
 * Initialize global toast system on page load
 * Call this in every page template via a script tag
 */
export function initToast() {
  // Create container if it doesn't exist
  let container = document.getElementById('toast-container')
  if (!container) {
    container = document.createElement('div')
    container.id = 'toast-container'
    document.body.appendChild(container)
  }

  // Render ToastManager component
  render(h(ToastManager), container)

  // Initialize window.showToast API
  initializeToastSystem()

  console.log('Toast system initialized. Use window.showToast() to show notifications.')
}

// Auto-initialize if document is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initToast)
} else {
  initToast()
}
