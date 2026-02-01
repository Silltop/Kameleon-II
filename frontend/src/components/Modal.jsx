export function Modal({ isOpen, title, children, onClose }) {
  return (
    <div
      className={`${
        isOpen ? '' : 'hidden'
      } fixed inset-0 bg-black bg-opacity-50 z-40 flex items-center justify-center`}
    >
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-md w-full m-4">
        <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
          <h5 className="text-lg font-semibold text-gray-900 dark:text-white">{title}</h5>
        </div>
        <div className="px-6 py-4 max-h-96 overflow-y-auto">{children}</div>
        <div className="px-6 py-4 border-t border-gray-200 dark:border-gray-700 text-right">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-gray-600 hover:bg-gray-700 dark:bg-gray-700 dark:hover:bg-gray-600 text-white rounded-md transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  )
}
