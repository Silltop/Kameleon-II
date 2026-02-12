export function Modal({ isOpen, title, children, onClose }) {
  return (
    <div
      className={`${
        isOpen ? '' : 'hidden'
      } fixed inset-0 bg-black/50 z-40 flex items-center justify-center`}
    >
      <div className="rounded-lg shadow-xl max-w-md w-full m-4 bg-base-100 text-base-content">
        <div className="px-6 py-4 border-b border-base-300">
          <h5 className="text-lg font-semibold">{title}</h5>
        </div>
        <div className="px-6 py-4 max-h-96 overflow-y-auto text-base-content/80">
          {children}
        </div>
        <div className="px-6 py-4 border-t border-base-300 text-right">
          <button
            onClick={onClose}
            className="btn"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  )
}
