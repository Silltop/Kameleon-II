import { useState, useEffect } from 'preact/hooks'

export function HostSummary({ hostDetailsList = [] }) {
  const [uptimeData, setUptimeData] = useState({})

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const response = await fetch('/uptime')
        if (response.ok) {
          const data = await response.json()
          setUptimeData(data)
        }
      } catch (error) {
        console.error('Failed to fetch uptime:', error)
      }
    }

    fetchStatus()
    const interval = setInterval(fetchStatus, 10000)
    return () => clearInterval(interval)
  }, [])

  const getStatusStyle = (hostIps) => {
    if (!hostIps || hostIps.length === 0) return { backgroundColor: 'red', boxShadow: '0 0 0 3px rgba(255, 51, 51, 0.8)' }
    
    for (const ip of hostIps) {
      const status = uptimeData[ip.ip]
      if (status && status.uptime && status.uptime !== 'Connection Error') {
        return { backgroundColor: 'green', boxShadow: '0 0 0 3px rgba(51, 255, 51, 0.8)' }
      }
    }
    
    return { backgroundColor: 'red', boxShadow: '0 0 0 3px rgba(255, 51, 51, 0.8)' }
  }

  // Helper to format date as dd.mm.yyyy HH:MM
  const formatDate = (dateString) => {
    const date = new Date(dateString)
    const pad = (n) => n.toString().padStart(2, '0')
    return `${pad(date.getDate())}.${pad(date.getMonth() + 1)}.${date.getFullYear()} ${pad(date.getHours())}:${pad(date.getMinutes())}`
  }

  return (
    <div className="w-full bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg m-8 p-8 text-black dark:text-gray-200">
      <h2 className="text-2xl font-bold mb-6 border-b border-gray-300 dark:border-gray-600 pb-3">
        Host Summary
      </h2>
      <p className="mb-2">
        <i className="fa fa-asterisk" aria-hidden="true"></i> Host private IP
        address are <span className="text-gray-500">grey</span>.
      </p>
      <p className="mb-4">
        <i className="fa fa-asterisk" aria-hidden="true"></i> IP addresses that
        are listed in RBL DB are marked in <span className="text-red-500">red</span>
        .
      </p>
      <div className="overflow-x-auto">
        <table className="w-full border-collapse">
          <thead>
            <tr className="border-b border-gray-300 dark:border-gray-600">
              <th className="text-left px-4 py-3 font-semibold">Hostname</th>
              <th className="text-left px-4 py-3 font-semibold">Distribution</th>
              <th className="text-left px-4 py-3 font-semibold">Kernel Version</th>
              <th className="text-left px-4 py-3 font-semibold">IP list</th>
              <th className="text-left px-4 py-3 font-semibold">User Count</th>
              <th className="text-left px-4 py-3 font-semibold">Disk devices</th>
              <th className="text-left px-4 py-3 font-semibold">Sync Time</th>
            </tr>
          </thead>
          <tbody>
            {hostDetailsList.map(({ host, facts }) => (
            <tr
              key={host.id}
              className="border-b border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
            >
              <th className="text-left px-4 py-3 font-normal">
                <i 
                  className="fa fa-power-off status-dot align-middle mr-2" 
                  style={getStatusStyle(host.host_ips)}
                ></i>
                {facts.hostname}
              </th>

              <td className="px-4 py-3">{facts.distro}</td>
              <td className="px-4 py-3">{facts.kernel}</td>

              <td className="px-4 py-3">
                <div className="overflow-y-auto max-h-20">
                  {host.host_ips?.map((ip) => (
                    <div
                      key={ip.ip}
                      className={`flex items-center ${
                        ip.is_listed
                          ? 'text-red-500'
                          : ip.is_private
                          ? 'text-gray-500'
                          : ''
                      }`}
                    >
                      {ip.ip}
                    </div>
                  ))}
                </div>
              </td>

              <td className="px-4 py-3">{facts.user_count}</td>

              <td className="px-4 py-3">
                <div className="overflow-y-auto max-h-20">
                  {host.host_devices?.map((device) => (
                    <div key={device.id}>{device.name}</div>
                  ))}
                </div>
              </td>

              <td className="px-4 py-3">
                {formatDate(facts.sync_timestamp)}
              </td>
            </tr>
          ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
