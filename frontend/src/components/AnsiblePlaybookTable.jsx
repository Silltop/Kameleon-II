import { useState, useEffect } from 'preact/hooks'

function getStatusBadge(status) {
  switch (status.toLowerCase()) {
    case "success":
      return (
        <span className="badge badge-success">
            <svg className="size-[1em]" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><g fill="currentColor" strokeLinejoin="miter" strokeLinecap="butt"><circle cx="12" cy="12" r="10" fill="none" stroke="currentColor" strokeLinecap="square" stroke-miterlimit="10" strokeWidth="2"></circle><polyline points="7 13 10 16 17 8" fill="none" stroke="currentColor" strokeLinecap="square" stroke-miterlimit="10" strokeWidth="2"></polyline></g></svg>
          Success
        </span>
      )
    case "unknown":
      return (
        <span className="badge badge-neutral">
          <svg className="size-[1em]" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M9.529 9.988a2.502 2.502 0 1 1 5 .191A2.441 2.441 0 0 1 12 12.582V14m-.01 3.008H12M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z"/></svg>
          Unknown
        </span>
      )
    case "failed":
      return (
        <span className="badge badge-error">
            <svg className="size-[1em]" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><g fill="currentColor"><rect x="1.972" y="11" width="20.056" height="2" transform="translate(-4.971 12) rotate(-45)" fill="currentColor" strokeWidth={0}></rect><path d="m12,23c-6.065,0-11-4.935-11-11S5.935,1,12,1s11,4.935,11,11-4.935,11-11,11Zm0-20C7.038,3,3,7.037,3,12s4.038,9,9,9,9-4.037,9-9S16.962,3,12,3Z" strokeWidth={0} fill="currentColor"></path></g></svg>
          Failure
        </span>
      )
    case "running":
      return (
        <span className="badge badge-info">
          <svg className="size-[1em]" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor"><path fillRule="evenodd" d="M8.6 5.2A1 1 0 0 0 7 6v12a1 1 0 0 0 1.6.8l8-6a1 1 0 0 0 0-1.6l-8-6Z" clipRule="evenodd"/></svg>
          Running
        </span>
      )
    default:
      return (
        <span className="badge badge-neutral">
          <svg className="size-[1em]" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M9.529 9.988a2.502 2.502 0 1 1 5 .191A2.441 2.441 0 0 1 12 12.582V14m-.01 3.008H12M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z"/></svg>
          Unknown
        </span>
      )
  }
}

export function AnsiblePlaybookTable({ tableData = [], onRunPlaybook, onShowRecentLog }) {
  const [statuses, setStatuses] = useState({})
  const [recentLogLoadingId, setRecentLogLoadingId] = useState(null)

  useEffect(() => {
    const updateStatuses = async () => {
      const newStatuses = {}
      for (const row of tableData) {
        try {
          const response = await fetch(`/ansible/recent_run_status/${row.id}`)
          const data = await response.json()
          newStatuses[row.id] = data.result
        } catch (error) {
          console.error(`Error updating playbook status for ${row.id}:`, error)
        }
      }
      setStatuses(newStatuses)
    }

    updateStatuses()
    const interval = setInterval(updateStatuses, 10000)
    return () => clearInterval(interval)
  }, [tableData])

  const handleRunPlaybook = async (playbookId) => {
    try {
      const response = await fetch(`/ansible/run_playbook/${playbookId}`)
      if (response.ok) {
        const data = await response.json()
        onRunPlaybook(data.run_id)
      }
    } catch (error) {
      console.error('Error starting playbook:', error)
    }
  }

  const handleShowRecentLog = async (playbookId) => {
    try {
      setRecentLogLoadingId(playbookId)
      const response = await fetch(`/ansible/recent_run/${playbookId}`)
      if (!response.ok) {
        const message = response.status === 404
          ? 'No recent runs found for this playbook'
          : 'Failed to fetch recent run'
        window.showToast?.error?.(message)
        return
      }
      const data = await response.json()
      if (data?.id) {
        onShowRecentLog?.(data.id)
      } else {
        window.showToast?.error?.('Recent run id is missing')
      }
    } catch (error) {
      console.error('Error fetching recent run:', error)
      window.showToast?.error?.('Failed to fetch recent run')
    } finally {
      setRecentLogLoadingId(null)
    }
  }

  return (
    <table className="table table-hover">
      <thead>
        <tr>
          <th>Playbook Name</th>
          <th>Status</th>
          <th>Started by</th>
          <th>Start</th>
          <th>Duration</th>
          <th>Options</th>
        </tr>
      </thead>
      <tbody>
        {tableData.map((row) => (
          <tr key={row.id} id={row.id}>
            <td>{row.playbook_name}</td>
            <td>{getStatusBadge(statuses[row.id] || row.status)}</td>
            <td>{row.started_by}</td>
            <td>{row.start}</td>
            <td>{row.duration}</td>
            <td>
              <button
                onClick={() => handleRunPlaybook(row.id)}
                className="btn btn-primary"
              >
                Run now
              </button>
              <button
                onClick={() => handleShowRecentLog(row.id)}
                className="btn btn-primary"
                disabled={recentLogLoadingId === row.id}
              >
                {recentLogLoadingId === row.id ? 'Loading...' : 'Show recent log'}
              </button>
              <a href={`/ansible/display_logs/${row.id}`}>
                <button className="btn btn-primary">Show historical logs</button>
              </a>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}
