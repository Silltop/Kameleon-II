import { useState, useEffect } from 'preact/hooks'
import '../assets/css/anim.css'
import { LoginModal } from './LoginModal'

const logoUrl = window.APP_CONFIG.logoUrl
const extensionRoutes = window.APP_CONFIG.extensionRoutes || []
const user = window.APP_CONFIG.user || null

export function Navbar() {
  const [isMobileOpen, setIsMobileOpen] = useState(false)
  const [isDark, setIsDark] = useState(() => {
    if (typeof window === 'undefined') return false
    return (
      localStorage.theme === 'dark' ||
      document.documentElement.classList.contains('dark') ||
      document.documentElement.dataset.theme === 'dark'
    )
  })

  useEffect(() => {
    const theme = isDark ? 'dark' : 'light'
    document.documentElement.dataset.theme = theme
    document.documentElement.classList.toggle('dark', isDark)
    localStorage.theme = theme
  }, [isDark])

  const toggleDarkMode = () => {
    setIsDark((prev) => !prev)
  }

  return (
    <div className="navbar bg-base-100 shadow-sm border-b border-base-300">
      
      {/* LEFT */}
      <div className="navbar-start">
        {/* Mobile Hamburger */}
        <div className="dropdown">
          <button
            tabIndex={0}
            className="btn btn-ghost lg:hidden"
            onClick={() => setIsMobileOpen(!isMobileOpen)}
          >
            <i className="fa fa-bars text-lg"></i>
          </button>

          {isMobileOpen && (
            <ul className="menu menu-sm dropdown-content mt-3 z-[1] p-2 shadow bg-base-100 rounded-box w-52">
              <li>
                <details>
                  <summary>Ansible</summary>
                  <ul className="p-2 bg-base-100 w-40 z-1">
                    <li><a href="/ansible/dashboard" >Dashboard</a></li>
                    <li><a href="/ansible/wrapper-configuration">Configuration</a></li>
                  </ul>
                </details>
              </li>

              <li>
                <details>
                  <summary>Reports</summary>
                  <ul className="p-2 bg-base-100 w-40 z-1">
                    <li><a href="/admin-functions">Admin Functions</a></li>
                  </ul>
                </details>
              </li>

              <li><a href="/configuration">Options</a></li>

              <li>
                <details>
                  <summary>Extensions</summary>
                  <ul>
                    {extensionRoutes.map((route) => (
                      <li key={route.route_endpoint}>
                        <a href={route.route_endpoint}>{route.route_name}</a>
                      </li>
                    ))}
                  </ul>
                </details>
              </li>
            </ul>
          )}
        </div>

        {/* Logo */}
        <a href="/" className="btn btn-ghost text-xl normal-case gap-3">
          <div
            className="mask_container w-8 h-8"
            style={{
              maskImage: `url(${logoUrl})`,
              WebkitMaskImage: `url(${logoUrl})`,
            }}
          />
          <span className="font-mono text-sm">Kameleon v.2</span>
        </a>
      </div>

      {/* CENTER (Desktop Menu) */}
      <div className="navbar-center hidden lg:flex">
        <ul className="menu menu-horizontal px-1">

          <li>
            <details>
              <summary>Ansible</summary>
              <ul className="p-2 bg-base-100 w-48 z-[1]">
                <li><a href="/ansible/dashboard">Dashboard</a></li>
                <li><a href="/ansible/wrapper-configuration">Configuration</a></li>
              </ul>
            </details>
          </li>

          <li>
            <details>
              <summary>Reports</summary>
              <ul className="p-2 bg-base-100 w-48 z-[1]">
                <li><a href="/admin-functions">Admin Functions</a></li>
              </ul>
            </details>
          </li>

          <li><a href="/configuration">Options</a></li>

          <li>
            <details>
              <summary>Extensions</summary>
              <ul className="p-2 bg-base-100 w-48 z-[1]">
                {extensionRoutes.map((route) => (
                  <li key={route.route_endpoint}>
                    <a href={route.route_endpoint}>{route.route_name}</a>
                  </li>
                ))}
              </ul>
            </details>
          </li>

        </ul>
      </div>

      {/* RIGHT */}
      <div className="navbar-end gap-2">
        <label className="flex cursor-pointer gap-2">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="20"
          height="20"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round">
          <circle cx="12" cy="12" r="5" />
          <path
            d="M12 1v2M12 21v2M4.2 4.2l1.4 1.4M18.4 18.4l1.4 1.4M1 12h2M21 12h2M4.2 19.8l1.4-1.4M18.4 5.6l1.4-1.4" />
        </svg>
        <input
          type="checkbox"
          value="dark"
          className="toggle theme-controller"
          checked={isDark}
          onChange={toggleDarkMode}
        />
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="20"
          height="20"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round">
          <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
        </svg>
      </label>
        {user?.user ? (
          <div className="dropdown dropdown-end">
            <button tabIndex={0} className="btn btn-ghost gap-2">
              <i className="fa fa-user"></i>
              <span className="font-mono">{user.preferred_username}</span>
            </button>

            <ul className="menu menu-sm dropdown-content mt-3 z-[1] p-2 shadow bg-base-100 rounded-box w-52">
              <li>
                <a href="/logout">
                  <i className="fa fa-sign-out-alt"></i> Log Out
                </a>
              </li>
            </ul>
          </div>
        ) : (
          <button 
            onClick={() => document.getElementById('login-modal').showModal()} 
            className="btn btn-primary btn-sm"
          >
            Log In
          </button>
        )}
      </div>
      <LoginModal />
    </div>
  )
}
