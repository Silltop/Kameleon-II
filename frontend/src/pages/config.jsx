import { render } from 'preact'
import { ConfigPage } from '../components/ConfigPage'
import '../index.css'

// Get data from window object (passed from Flask template)
const initialContent = window.__APP_STATE__?.fileContent || ''

render(
  <ConfigPage initialContent={initialContent} />,
  document.getElementById('app')
)
