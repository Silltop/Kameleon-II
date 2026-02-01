import { render } from 'preact'
import './index.css'
import { App } from './app.jsx'

// Initialize dark mode if stored
if (localStorage.theme === 'dark' || (!('theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
  document.documentElement.classList.add('dark')
} else {
  document.documentElement.classList.remove('dark')
}

render(<App />, document.getElementById('app'))
