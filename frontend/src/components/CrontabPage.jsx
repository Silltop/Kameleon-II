export function CrontabPage({ results = {} }) {
  return (
    <div className="flex flex-wrap gap-6 p-6">
      {Object.entries(results).map(([host, result]) => (
        <div
          key={host}
          className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow p-6 w-full sm:w-80"
        >
          <h3 className="text-lg font-bold text-gray-900 dark:text-white border-b border-gray-300 dark:border-gray-600 pb-3 mb-4">
            {host}
          </h3>
          <div className="space-y-2 text-sm text-gray-700 dark:text-gray-300">
            {result.map((entry, idx) => (
              <div key={idx}>
                <div>{entry}</div>
                <hr className="border-gray-200 dark:border-gray-700" />
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  )
}
