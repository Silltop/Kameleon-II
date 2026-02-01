import { Navbar } from './Navbar'
import { Footer } from './Footer'

export function Layout({ children, extensionRoutes = [], user = null }) {
  return (
    <div className="flex flex-col min-h-screen">
      <Navbar extensionRoutes={extensionRoutes} user={user} />
      <main className="flex-1">{children}</main>
      <Footer />
    </div>
  )
}
