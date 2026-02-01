import { h, render } from 'preact'
import { Navbar } from '../components/Navbar'

const container = document.getElementById('navbar-container')
if (container) {
  render(h(Navbar), container)
}