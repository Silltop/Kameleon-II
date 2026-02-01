import { render } from 'preact'
import { AnsibleDashboard } from '../components/AnsibleDashboard'
import '../index.css'

// Get data from window object (passed from Flask template)
const tableData = window.__APP_STATE__?.tableData || []

render(
  <AnsibleDashboard tableData={tableData} />,
  document.getElementById('app')
)
