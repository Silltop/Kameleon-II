import { render } from 'preact'
import { Dashboard } from '../components/Dashboard'
import '../index.css'

// Get data from window object (passed from Flask template)
const hostDetailsList = window.__APP_STATE__?.hostDetailsList || []
const charts = window.__APP_STATE__?.charts || []

render(
  <Dashboard hostDetailsList={hostDetailsList} charts={charts} />,
  document.getElementById('app')
)
