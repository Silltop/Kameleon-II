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
  const [runStatus, setRunStatus] = useState('starting')
  const logContainerRef = useRef(null)
  const eventSourceRef = useRef(null)
  const statusPollRef = useRef(null)

  const getStatusBadge = (status) => {
    const normalized = (status || 'unknown').toLowerCase()
    switch (normalized) {
      case 'success':
        return <span className="badge badge-success">Success</span>
      case 'failed':
      case 'failure':
      case 'error':
        return <span className="badge badge-error">Failure</span>
      case 'running':
        return <span className="badge badge-info">Running</span>
      case 'starting':
        return <span className="badge badge-neutral">Starting</span>
      default:
        return <span className="badge badge-neutral">Unknown</span>
    }
  }

  const extractResultFromCloseEvent = (message) => {
    if (!message) return 'unknown'
    const match = message.match(/result:\s*([a-zA-Z_]+)/)
    return match ? match[1].toLowerCase() : 'unknown'
  }

  useEffect(() => {
    if (isOpen && runId) {
      setIsLoading(true)
      setLogs([])
      setRunStatus('running')

      const fetchRunStatus = async () => {
        try {
          const response = await fetch(`/ansible/run_status/${runId}`)
          if (!response.ok) return
          const data = await response.json()
          if (data?.result) {
            setRunStatus(data.result.toLowerCase())
            if (data.result.toLowerCase() !== 'running' && statusPollRef.current) {
              clearInterval(statusPollRef.current)
              statusPollRef.current = null
            }
          }
        } catch (error) {
          console.error('Error fetching run status:', error)
        }
      }

      fetchRunStatus()
      statusPollRef.current = setInterval(fetchRunStatus, 2000)

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
        setRunStatus('failed')
        setIsLoading(false)
        if (statusPollRef.current) {
          clearInterval(statusPollRef.current)
          statusPollRef.current = null
        }
      }

      eventSource.addEventListener('close', function (event) {
        console.log('Stream closed:', event.data)
        eventSource.close()
        setRunStatus(extractResultFromCloseEvent(event.data))
        setIsLoading(false)
        if (statusPollRef.current) {
          clearInterval(statusPollRef.current)
          statusPollRef.current = null
        }
      })

      return () => {
        if (eventSourceRef.current) {
          eventSourceRef.current.close()
        }
        if (statusPollRef.current) {
          clearInterval(statusPollRef.current)
          statusPollRef.current = null
        }
      }
    }
  }, [runId, isOpen])

  useEffect(() => {
    if (isOpen && !runId) {
      setLogs([])
      setIsLoading(true)
      setRunStatus('starting')
    }
  }, [isOpen, runId])

  useEffect(() => {
    if (logContainerRef.current) {
      logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight
    }
  }, [logs])

  if (!isOpen) return null

  return (
    <div className="modal modal-open" role="dialog">
      <div className="modal-box w-11/12 max-w-4xl">
        <div className="flex items-center gap-3">
          <h5 className="text-lg font-semibold">Ansible Playbook Logs</h5>
          {getStatusBadge(runStatus)}
        </div>
        <div
          ref={logContainerRef}
          className="mt-4 max-h-[800px] overflow-y-auto"
        >
          {isLoading && (
            <div>
              <div className="loading-spinner"></div>
              {runId ? 'Loading logs...' : 'Starting playbook...'}
            </div>
          )}
          {logs.map((log, index) => (
            <p key={index} dangerouslySetInnerHTML={{ __html: log }}></p>
          ))}
          {runStatus === 'running' && !isLoading && (
            <p className="mt-2">Running<span className="ellipsis"></span></p>
          )}
        </div>
        <div className="modal-action">
          <button className="btn" onClick={onClose} role="button">
            Close
          </button>
        </div>
      </div>
    </div>
  )
}
