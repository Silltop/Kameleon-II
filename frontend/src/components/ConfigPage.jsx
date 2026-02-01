import { useState } from 'preact/hooks'

export function ConfigPage({ initialContent = '' }) {
  const [isOpen, setIsOpen] = useState(false)
  const [content, setContent] = useState(initialContent)
  const [isSaving, setIsSaving] = useState(false)

  const handleSave = async () => {
    setIsSaving(true)
    try {
      const response = await fetch('/saveContent', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ content }),
      })
      if (response.ok) {
        window.showNotification?.('Configuration saved successfully', 'success')
      } else {
        window.showNotification?.('Failed to save configuration', 'error')
      }
    } catch (error) {
      console.error('Save failed:', error)
      window.showNotification?.('Error saving configuration', 'error')
    } finally {
      setIsSaving(false)
    }
  }

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <details
        className="group bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow"
        open={isOpen}
        onToggle={() => setIsOpen(!isOpen)}
      >
        <summary className="flex cursor-pointer items-center justify-between p-6 font-semibold text-gray-900 dark:text-white hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
          <span className="flex items-center gap-2">
            Managed hosts file <i className="fas fa-edit ml-2"></i>
          </span>
          <span className="transition-transform group-open:rotate-180">
            <i className="fa fa-chevron-down"></i>
          </span>
        </summary>
        <div className="border-t border-gray-200 dark:border-gray-700 px-6 py-4">
          <textarea
            value={content}
            onChange={(e) => setContent(e.currentTarget.value)}
            className="w-full h-96 px-4 py-2 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-sm"
            placeholder="Edit configuration here..."
          />
          <button
            onClick={handleSave}
            disabled={isSaving}
            className="mt-4 px-4 py-2 bg-blue-600 hover:bg-blue-700 dark:bg-blue-700 dark:hover:bg-blue-600 text-white rounded-md transition-colors flex items-center gap-2 disabled:opacity-50"
          >
            <i className="fa-solid fa-floppy-disk"></i>
            {isSaving ? 'Saving...' : 'Save'}
          </button>
        </div>
      </details>
    </div>
  )
}
