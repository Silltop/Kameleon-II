import { useState, useEffect, useRef } from 'preact/hooks'

export function LogStream({ ansibleRunId, autoScroll = true }) {
  const [logs, setLogs] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [isStreamOpen, setIsStreamOpen] = useState(false)
  const logContainerRef = useRef(null)
  const eventSourceRef = useRef(null)

  useEffect(() => {
    if (!ansibleRunId) {
      setError('Ansible Run ID is required')
      setLoading(false)
      return
    }

    startLogStream()

    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close()
      }
    }
  }, [ansibleRunId])

  useEffect(() => {
    if (autoScroll && logContainerRef.current) {
      logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight
    }
  }, [logs, autoScroll])

  const decodeBase64 = (encodedMessage) => {
    try {
      return atob(encodedMessage)
    } catch (err) {
      console.error('Failed to decode Base64:', err)
      return encodedMessage
    }
  }

  const highlightKeywords = (text) => {
    const keywords = [
      { word: 'fatal', class: 'text-red-700 dark:text-red-300 font-bold' },
      { word: 'error', class: 'text-red-600 dark:text-red-400' },
      { word: 'failed', class: 'text-red-600 dark:text-red-400' },
      { word: 'warning', class: 'text-yellow-600 dark:text-yellow-400' },
      { word: 'success', class: 'text-green-600 dark:text-green-400' },
      { word: 'ok', class: 'text-green-600 dark:text-green-400' },
    ]

    let highlightedText = text
    keywords.forEach(({ word, class: className }) => {
      const regex = new RegExp(`\\b${word}\\b`, 'gi')
      highlightedText = highlightedText.replace(
        regex,
        (match) => `<span class="${className}">${match}</span>`
      )
    })

    return highlightedText
  }

  const startLogStream = () => {
    setLoading(true)
    setError(null)
    setLogs([])
    setIsStreamOpen(true)

    const eventSource = new EventSource(`/ansible/logs-stream/${ansibleRunId}`)
    eventSourceRef.current = eventSource

    eventSource.onmessage = (event) => {
      const decodedLog = decodeBase64(event.data)
      setLogs((prevLogs) => [
        ...prevLogs,
        {
          id: Date.now(),
          text: decodedLog,
          highlighted: highlightKeywords(decodedLog),
        },
      ])
      setLoading(false)
    }

    eventSource.addEventListener('close', () => {
      console.log('Log stream closed')
      setIsStreamOpen(false)
      eventSource.close()
    })

    eventSource.onerror = (err) => {
      console.error('Error in log stream:', err)
      setError('Failed to fetch logs. Stream closed.')
      setIsStreamOpen(false)
      eventSource.close()
    }
  }

  const handleRetry = () => {
    startLogStream()
  }

  const handleClear = () => {
    setLogs([])
  }

  return (
    <div className="flex flex-col h-full gap-4">
      {/* Controls */}
      <div className="flex gap-2 items-center">
        <button
          onClick={handleRetry}
          disabled={isStreamOpen}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white rounded-lg text-sm font-medium transition"
        >
          {isStreamOpen ? 'Streaming...' : 'Reconnect'}
        </button>
        <button
          onClick={handleClear}
          className="px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg text-sm font-medium transition"
        >
          Clear
        </button>
        <div className="flex-1"></div>
        {isStreamOpen && (
          <div className="flex items-center gap-2">
            <i className="fa-solid fa-spinner animate-spin text-blue-600"></i>
            <span className="text-sm text-gray-600 dark:text-gray-400">Streaming...</span>
          </div>
        )}
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border border-red-200 dark:bg-red-900 dark:border-red-700 rounded-lg p-4 text-red-800 dark:text-red-100">
          <p className="font-semibold flex items-center gap-2">
            <i className="fa-solid fa-circle-xmark"></i>
            {error}
          </p>
        </div>
      )}

      {/* Log Container */}
      <div
        ref={logContainerRef}
        className="flex-1 overflow-y-auto bg-gray-900 dark:bg-black rounded-lg p-4 font-mono text-sm border border-gray-700 dark:border-gray-800"
      >
        {loading && logs.length === 0 ? (
          <div className="flex items-center justify-center h-full gap-2 text-gray-400">
            <i className="fa-solid fa-spinner animate-spin"></i>
            <span>Loading logs...</span>
          </div>
        ) : logs.length === 0 ? (
          <div className="text-gray-500 text-center py-8">No logs to display</div>
        ) : (
          logs.map((log) => (
            <div
              key={log.id}
              className="text-gray-300 hover:bg-gray-800 dark:hover:bg-gray-900 px-2 py-1 rounded"
            >
              <p dangerouslySetInnerHTML={{ __html: log.highlighted }} />
            </div>
          ))
        )}
      </div>
    </div>
  )
}

export function LogModal({ ansibleRunId, isOpen, onClose }) {
  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 dark:bg-opacity-70 z-50 flex items-center justify-center p-4">
      <div className="bg-white dark:bg-gray-900 rounded-lg shadow-lg max-w-4xl w-full h-[600px] flex flex-col">
        <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-xl font-semibold">Playbook Logs</h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
          >
            <i className="fa-solid fa-xmark text-2xl"></i>
          </button>
        </div>
        <div className="flex-1 p-6 overflow-hidden">
          <LogStream ansibleRunId={ansibleRunId} />
        </div>
      </div>
    </div>
  )
}

// usage
// import { LogStream, LogModal } from '../components/LogStream'
// import { useState } from 'preact/hooks'

// // Inline
// <LogStream ansibleRunId="run-123" />

// // In modal
// const [showLogs, setShowLogs] = useState(false)
// return (
//   <>
//     <button onClick={() => setShowLogs(true)}>View Logs</button>
//     <LogModal ansibleRunId="run-123" isOpen={showLogs} onClose={() => setShowLogs(false)} />
//   </>
// )