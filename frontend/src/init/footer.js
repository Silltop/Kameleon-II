import { h, render } from 'preact'
import { Footer } from '../components/Footer'

const container = document.getElementById('footer-container')
if (container) {
  render(h(Footer), container)
}