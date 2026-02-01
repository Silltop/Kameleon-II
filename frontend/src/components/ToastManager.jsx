import { h } from 'preact'
import { useState, useCallback } from 'preact/hooks'
import { Toast } from './Toast'

export function ToastManager() {
  const [toasts, setToasts] = useState([])

  const addToast = useCallback((message, type = 'info', duration = 7500) => {
    const id = Date.now()
    setToasts((prev) => [...prev, { id, message, type, duration }])

    // Auto-remove toast after duration
    if (duration > 0) {
      setTimeout(() => {
        setToasts((prev) => prev.filter((t) => t.id !== id))
      }, duration)
    }

    return id
  }, [])

  const removeToast = useCallback((id) => {
    setToasts((prev) => prev.filter((t) => t.id !== id))
  }, [])

  // Expose globally
  if (!window.__toastManager) {
    window.__toastManager = { addToast, removeToast }
  }

  return (
    <div className="fixed top-4 right-4 z-50 space-y-2 pointer-events-none">
      {toasts.map((toast) => (
        <div key={toast.id} className="pointer-events-auto">
          <Toast message={toast.message} type={toast.type} duration={toast.duration} />
        </div>
      ))}
    </div>
  )
}
