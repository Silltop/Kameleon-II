export function AnsibleInventoryPage({ inventory = {} }) {
  return (
    <div className="flex flex-wrap gap-6 p-6">
      {Object.entries(inventory).map(([groupName, values]) => (
        <div
          key={groupName}
          className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow p-6 w-full sm:w-80"
        >
          <h3 className="text-lg font-bold text-gray-900 dark:text-white border-b border-gray-300 dark:border-gray-600 pb-3 mb-4">
            {groupName}
          </h3>
          <div className="space-y-3 text-sm text-gray-700 dark:text-gray-300">
            {Object.entries(values.hosts || {}).map(([hostname, hostValues]) => (
              <div key={hostname}>
                <p className="font-semibold text-gray-900 dark:text-white">{hostname}</p>
                <ul className="ml-4 space-y-1">
                  {Object.entries(hostValues).map(([key, value]) => (
                    <li key={key} className="text-gray-600 dark:text-gray-400">
                      {key}: {value}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  )
}
