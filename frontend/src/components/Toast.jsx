import { useState, useEffect } from 'preact/hooks'

export function Toast({ message, type = 'info', duration = 7500 }) {
  const [isVisible, setIsVisible] = useState(true)

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsVisible(false)
    }, duration)

    return () => clearTimeout(timer)
  }, [duration])

  if (!isVisible) return null

  const bgColor = {
    info: 'bg-blue-50 dark:bg-blue-900 border-blue-200 dark:border-blue-700 text-blue-800 dark:text-blue-100',
    success: 'bg-green-50 dark:bg-green-900 border-green-200 dark:border-green-700 text-green-800 dark:text-green-100',
    error: 'bg-red-50 dark:bg-red-900 border-red-200 dark:border-red-700 text-red-800 dark:text-red-100',
    warning: 'bg-yellow-50 dark:bg-yellow-900 border-yellow-200 dark:border-yellow-700 text-yellow-800 dark:text-yellow-100',
  }[type] || bgColor['info']

  return (
    <div
      className={`fixed top-4 right-4 z-50 max-w-md animate-fade-in-down border rounded-lg p-4 ${bgColor}`}
      style={{ opacity: isVisible ? 1 : 0, transition: 'opacity 0.3s ease' }}
    >
      <h4 className="font-semibold mb-1">Notification</h4>
      <p>{message}</p>
    </div>
  )
}
