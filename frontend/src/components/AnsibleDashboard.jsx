import { useState } from 'preact/hooks'
import { AnsiblePlaybookTable } from './AnsiblePlaybookTable'
import { AnsibleLogModal } from './AnsibleLogModal'

export function AnsibleDashboard({ tableData = [] }) {
  const [modalOpen, setModalOpen] = useState(false)
  const [currentRunId, setCurrentRunId] = useState(null)

  const handleRunPlaybook = (runId) => {
    setCurrentRunId(runId)
    setModalOpen(true)
  }

  const handleShowRecentLog = (runId) => {
    setCurrentRunId(runId)
    setModalOpen(true)
  }

  const handleCloseModal = () => {
    setModalOpen(false)
    setCurrentRunId(null)
    window.location.reload()
  }

  return (
    <div>
      <AnsiblePlaybookTable
        tableData={tableData}
        onRunPlaybook={handleRunPlaybook}
        onShowRecentLog={handleShowRecentLog}
      />
      <AnsibleLogModal
        runId={currentRunId}
        isOpen={modalOpen}
        onClose={handleCloseModal}
      />
    </div>
  )
}
