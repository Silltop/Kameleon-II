import { render } from 'preact'
import { AnsibleInventoryPage } from '../components/AnsibleInventoryPage'
import '../index.css'

// Get data from window object (passed from Flask template)
const inventory = window.__APP_STATE__?.inventory || {}

render(
  <AnsibleInventoryPage inventory={inventory} />,
  document.getElementById('app')
)
