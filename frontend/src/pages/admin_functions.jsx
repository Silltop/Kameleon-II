import { render } from 'preact'
import { AdminFunctions } from '../components/AdminFunctions'
import '../index.css'

const hostList = window.__APP_STATE__?.hostList || []
const functions = window.__APP_STATE__?.functions || []

render(
  <AdminFunctions hostList={hostList} functions={functions} />,
  document.getElementById('app')
)
