import { useMemo, useState } from 'preact/hooks'
import { Modal } from './Modal'

function statusToBadge(status) {
  const normalized = (status || '').toString().toLowerCase()
  if (normalized === 'ok' || normalized === 'success') return 'badge-success'
  if (normalized === 'nok' || normalized === 'failed') return 'badge-error'
  return 'badge-neutral'
}

function AdminFunctionCard({
  functionItem,
  hostList,
  selectedHost,
  onHostChange,
  onRun,
  isRunning,
}) {
  return (
    <div className="card bg-base-100 shadow border border-base-300">
      <div className="card-body gap-4">
        <div className="space-y-2">
          <h3 className="card-title text-lg">{functionItem.title}</h3>
          <p className="text-sm text-base-content/70">
            {functionItem.description}
          </p>
        </div>
        <div className="flex flex-wrap items-end gap-4 justify-end">
          <label className="form-control w-full sm:w-64">
            <div className="label">
              <span className="label-text">Hosts</span>
            </div>
            <select
              className="select select-bordered"
              value={selectedHost}
              onChange={(event) => onHostChange(event.currentTarget.value)}
              required
            >
              <option value="all">All</option>
              {hostList.map((host) => (
                <option key={host} value={host}>{host}</option>
              ))}
            </select>
          </label>
          <button
            type="button"
            className="btn btn-primary"
            onClick={onRun}
            disabled={isRunning}
          >
            {isRunning ? 'Running...' : 'Run'}
          </button>
        </div>
      </div>
    </div>
  )
}

export function AdminFunctions({ hostList = [], functions = [] }) {
  const [selectedHosts, setSelectedHosts] = useState({})
  const [modalOpen, setModalOpen] = useState(false)
  const [activeFunction, setActiveFunction] = useState(null)
  const [results, setResults] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const [runningId, setRunningId] = useState(null)

  const functionList = useMemo(() => {
    return (functions || []).filter((item) => item && item.endpoint)
  }, [functions])

  const getFunctionId = (functionItem) => {
    return functionItem.id || functionItem.endpoint || functionItem.title
  }

  const handleHostChange = (functionId, host) => {
    setSelectedHosts((prev) => ({ ...prev, [functionId]: host }))
  }

  const handleRun = async (functionItem) => {
    const functionId = getFunctionId(functionItem)
    const host = selectedHosts[functionId] || 'all'
    setActiveFunction(functionItem)
    setModalOpen(true)
    setIsLoading(true)
    setError('')
    setResults([])
    setRunningId(functionId)

    try {
      const response = await fetch(functionItem.endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify({ host }),
      })

      if (!response.ok) {
        throw new Error('Failed to run admin function')
      }

      const data = await response.json()
      setResults(data.results || [])
    } catch (err) {
      console.error('Admin function failed:', err)
      setError('Failed to run admin function')
      window.showToast?.error?.('Failed to run admin function')
    } finally {
      setIsLoading(false)
      setRunningId(null)
    }
  }

  const closeModal = () => {
    setModalOpen(false)
    setResults([])
    setError('')
  }

  return (
    <div className="max-w-5xl mx-auto p-6 space-y-6">
      {functionList.map((functionItem) => (
        <AdminFunctionCard
          key={getFunctionId(functionItem)}
          functionItem={functionItem}
          hostList={hostList}
          selectedHost={selectedHosts[getFunctionId(functionItem)] || 'all'}
          onHostChange={(host) => handleHostChange(getFunctionId(functionItem), host)}
          onRun={() => handleRun(functionItem)}
          isRunning={runningId === getFunctionId(functionItem)}
        />
      ))}

      <Modal
        isOpen={modalOpen}
        title={activeFunction?.title || 'Execution Status'}
        onClose={closeModal}
      >
        {isLoading && (
          <div className="flex items-center gap-2 text-sm text-base-content/70">
            <span className="loading loading-spinner"></span>
            Running...
          </div>
        )}
        {error && (
          <div className="alert alert-error text-sm">
            <span>{error}</span>
          </div>
        )}
        {!isLoading && !error && results.length === 0 && (
          <p className="text-sm text-base-content/70">No results returned.</p>
        )}
        <div className="space-y-4">
          {results.map(([host, status, details]) => (
            <div key={`${host}-${status}`} className="space-y-1">
              <div className="flex flex-wrap items-center gap-2">
                <span className="font-semibold">{host}</span>
                <span className={`badge ${statusToBadge(status)}`}>
                  {status}
                </span>
              </div>
              {details && (
                <p className="text-xs text-base-content/70">{details}</p>
              )}
              <div className="divider my-2"></div>
            </div>
          ))}
        </div>
      </Modal>
    </div>
  )
}
