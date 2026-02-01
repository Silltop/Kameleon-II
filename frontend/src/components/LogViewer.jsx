import { useState, useEffect, useRef } from 'preact/hooks'
import { EditorView, basicSetup } from 'codemirror'
import { EditorState } from '@codemirror/state'
import { javascript } from '@codemirror/lang-javascript'
import { oneDark } from '@codemirror/theme-one-dark'

const themes = {
  light: [],
  dark: [oneDark],
}

export function LogViewer({ playbookId }) {
  const [logs, setLogs] = useState([])
  const [selectedRun, setSelectedRun] = useState('latest')
  const [theme, setTheme] = useState(() => {
    return document.documentElement.dataset.theme === 'dark' ||
           document.documentElement.classList.contains('dark')
      ? 'dark'
      : 'light'
  })
  const editorRef = useRef(null)
  const viewRef = useRef(null)

  // Watch for theme changes
  useEffect(() => {
    const observer = new MutationObserver(() => {
      const isDark = document.documentElement.dataset.theme === 'dark' ||
                     document.documentElement.classList.contains('dark')
      setTheme(isDark ? 'dark' : 'light')
    })

    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ['data-theme', 'class'],
    })

    return () => observer.disconnect()
  }, [])

  // Initialize CodeMirror
  useEffect(() => {
    if (!editorRef.current) return

    const state = EditorState.create({
      doc: '',
      extensions: [
        basicSetup,
        javascript(),
        EditorView.editable.of(false),
        EditorView.lineWrapping,
        ...themes[theme],
      ],
    })

    const view = new EditorView({
      state,
      parent: editorRef.current,
    })

    viewRef.current = view

    return () => {
      view.destroy()
    }
  }, [theme])

  // Update editor content when logs change
  useEffect(() => {
    if (viewRef.current && logs.length > 0) {
      const content = logs.join('\n')
      viewRef.current.dispatch({
        changes: {
          from: 0,
          to: viewRef.current.state.doc.length,
          insert: content,
        },
      })
    }
  }, [logs])

  // Fetch logs
  const fetchLogs = async () => {
    try {
      const response = await fetch(`/ansible/logs/${playbookId}`)
      if (response.ok) {
        const data = await response.json()
        setLogs(data)
      }
    } catch (error) {
      console.error('Error fetching logs:', error)
    }
  }

  // Initial fetch and polling
  useEffect(() => {
    fetchLogs()
    const interval = setInterval(fetchLogs, 5000)
    return () => clearInterval(interval)
  }, [playbookId, selectedRun])

  return (
    <div className="p-6 flex flex-col h-full">
      <h2 className="text-xl font-bold mb-4">Playbook Logs</h2>
      <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
        Logs will update every 5 seconds
      </p>

      <div className="flex gap-4 mb-4">
        <div className="flex-1">
          <label className="block text-sm font-medium mb-2">Select Run</label>
          <select
            className="select select-bordered w-full"
            value={selectedRun}
            onChange={(e) => setSelectedRun(e.target.value)}
          >
            <option value="latest">Latest</option>
          </select>
        </div>
      </div>

      <div
        ref={editorRef}
        className="border border-gray-300 dark:border-gray-700 rounded-lg overflow-hidden flex-1"
        style={{ minHeight: '500px', height: 'auto' }}
      ></div>
    </div>
  )
}
