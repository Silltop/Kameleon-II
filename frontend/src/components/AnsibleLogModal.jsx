import { useState, useEffect, useRef } from 'preact/hooks'

function decodeBase64(encodedMessage) {
  return atob(encodedMessage)
}

function highlightKeywords(logMessage) {
  const keywords = {
    'fatal': 'fatal',
    'error': 'error',
    'warning': 'warning',
    'failed!': 'fatal'
  }

  return logMessage.replace(
    new RegExp(Object.keys(keywords).join("|"), "gi"),
    (match) => {
      const lowerMatch = match.toLowerCase()
      if (lowerMatch === 'fatal' || lowerMatch === 'failed!') {
        return `<span class="fatal">${match}</span>`
      } else if (lowerMatch === 'error') {
        return `<span class="red">${match}</span>`
      } else if (lowerMatch === 'warning') {
        return `<span class="orange">${match}</span>`
      }
      return match
    }
  )
}

export function AnsibleLogModal({ runId, isOpen, onClose }) {
  const [logs, setLogs] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const logContainerRef = useRef(null)
  const eventSourceRef = useRef(null)

  useEffect(() => {
    if (isOpen && runId) {
      setIsLoading(true)
      setLogs([])

      const eventSource = new EventSource(`/ansible/logs-stream/${runId}`)
      eventSourceRef.current = eventSource

      eventSource.onmessage = function (event) {
        const decodedLog = decodeBase64(event.data)
        const highlighted = highlightKeywords(decodedLog)
        setLogs((prevLogs) => [...prevLogs, highlighted])
        setIsLoading(false)
      }

      eventSource.onerror = function (event) {
        console.error('Error fetching logs:', event)
        eventSource.close()
        setIsLoading(false)
      }

      eventSource.addEventListener('close', function (event) {
        console.log('Stream closed:', event.data)
        eventSource.close()
        setIsLoading(false)
      })

      return () => {
        if (eventSourceRef.current) {
          eventSourceRef.current.close()
        }
      }
    }
  }, [runId, isOpen])

  useEffect(() => {
    if (logContainerRef.current) {
      logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight
    }
  }, [logs])

  if (!isOpen) return null

  return (
    <div className="modal" style={{ display: 'block' }} tabIndex="-1" role="dialog">
      <div className="modal-dialog" role="document">
        <div className="modal-content" style={{ width: '50vw' }}>
          <h5 className="modal-title">Ansible Playbook Logs</h5>
          <div
            ref={logContainerRef}
            className="modal-body"
            style={{ maxHeight: '800px', overflowY: 'auto' }}
          >
            {isLoading && (
              <div>
                <div className="loading-spinner"></div>
                Loading...
              </div>
            )}
            {logs.map((log, index) => (
              <p key={index} dangerouslySetInnerHTML={{ __html: log }}></p>
            ))}
          </div>
          <div className="text-right mt-20">
            <button className="btn mr-5" onClick={onClose} role="button">
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
