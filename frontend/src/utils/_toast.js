/**
 * Global Toast notification system
 * Provides window.showToast() API for templates and JavaScript
 */

export function initializeToastSystem() {
  window.showToast = function (message, type = 'info', duration = 7500) {
    if (window.__toastManager) {
      return window.__toastManager.addToast(message, type, duration)
    } else {
      console.warn('Toast manager not initialized. Make sure ToastManager component is mounted.')
    }
  }

  window.showToast.info = (message, duration) => window.showToast(message, 'info', duration)
  window.showToast.success = (message, duration) => window.showToast(message, 'success', duration)
  window.showToast.error = (message, duration) => window.showToast(message, 'error', duration)
  window.showToast.warning = (message, duration) => window.showToast(message, 'warning', duration)
}

export function removeToast(id) {
  if (window.__toastManager) {
    window.__toastManager.removeToast(id)
  }
}
