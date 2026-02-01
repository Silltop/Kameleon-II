import { render } from 'preact'
import { CrontabPage } from '../components/CrontabPage'
import '../index.css'

// Get data from window object (passed from Flask template)
const results = window.__APP_STATE__?.results || {}

render(
  <CrontabPage results={results} />,
  document.getElementById('app')
)
