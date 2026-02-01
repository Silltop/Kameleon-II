import { h, render } from 'preact'
import { LogViewer } from '../components/LogViewer'
import '../index.css'

const container = document.getElementById('log-viewer-container')
if (container) {
  const playbookId = window.__APP_STATE__?.playbookId
  if (playbookId) {
    render(h(LogViewer, { playbookId }), container)
  }
}
