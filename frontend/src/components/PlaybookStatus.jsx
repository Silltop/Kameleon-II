import { useState, useEffect } from 'preact/hooks'

export function PlaybookStatusBadge({ playbookID, onStatusUpdate }) {
  const [status, setStatus] = useState('unknown')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    updateStatus()
  }, [playbookID])

  const updateStatus = async () => {
    try {
      setLoading(true)
      const response = await fetch(`/ansible/recent_run_status/${playbookID}`)
      const data = await response.json()
      setStatus(data.result || 'unknown')
      setError(null)
      onStatusUpdate?.(data.result)
    } catch (err) {
      console.error('Error fetching playbook status:', err)
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const getStatusStyles = (status) => {
    const statusMap = {
      success: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-100 border border-green-300 dark:border-green-700',
      failed: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-100 border border-red-300 dark:border-red-700',
      running: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-100 border border-blue-300 dark:border-blue-700',
      unknown: 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-100 border border-gray-300 dark:border-gray-600',
    }
    return statusMap[status.toLowerCase()] || statusMap.unknown
  }

  const getStatusIcon = (status) => {
    const iconMap = {
      success: 'fa-circle-check',
      failed: 'fa-circle-xmark',
      running: 'fa-forward',
      unknown: 'fa-circle-question',
    }
    return iconMap[status.toLowerCase()] || iconMap.unknown
  }

  const getStatusLabel = (status) => {
    const labelMap = {
      success: 'Success',
      failed: 'Failure',
      running: 'Running',
      unknown: 'Unknown',
    }
    return labelMap[status.toLowerCase()] || 'Unknown'
  }

  if (error) {
    return (
      <span className="bg-red-50 text-red-700 dark:bg-red-900 dark:text-red-100 px-3 py-1 rounded-lg text-sm">
        Error
      </span>
    )
  }

  return (
    <div className="flex items-center gap-2">
      <span className={`inline-flex items-center gap-2 px-3 py-1 rounded-lg text-sm font-medium ${getStatusStyles(status)}`}>
        <i className={`fa-solid ${getStatusIcon(status)}`}></i>
        {getStatusLabel(status)}
      </span>
      {loading && <i className="fa-solid fa-spinner animate-spin"></i>}
    </div>
  )
}

export function PlaybookStatusTable({ playbooks }) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full border-collapse">
        <thead>
          <tr className="bg-gray-100 dark:bg-gray-700">
            <th className="border border-gray-300 dark:border-gray-600 px-4 py-2 text-left">Playbook ID</th>
            <th className="border border-gray-300 dark:border-gray-600 px-4 py-2 text-left">Status</th>
          </tr>
        </thead>
        <tbody>
          {playbooks.map((playbook) => (
            <tr key={playbook.id} id={playbook.id} className="hover:bg-gray-50 dark:hover:bg-gray-800">
              <td className="border border-gray-300 dark:border-gray-600 px-4 py-2">{playbook.name}</td>
              <td className="border border-gray-300 dark:border-gray-600 px-4 py-2">
                <PlaybookStatusBadge 
                  playbookID={playbook.id}
                  onStatusUpdate={(newStatus) => {
                    console.log(`Playbook ${playbook.id} updated to: ${newStatus}`)
                  }}
                />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

// to use it

// import { PlaybookStatusBadge, PlaybookStatusTable } from '../components/PlaybookStatus'

// // Single badge
// <PlaybookStatusBadge playbookID="123" />

// // Full table
// <PlaybookStatusTable playbooks={[
//   { id: '1', name: 'hello_world' },
//   { id: '2', name: 'simulate_error' }
// ]} />
