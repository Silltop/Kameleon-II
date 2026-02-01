import { defineConfig } from 'vite'
import preact from '@preact/preset-vite'
import tailwindcss from '@tailwindcss/vite'
import { readdirSync } from 'fs'
import { resolve } from 'path'
import { fileURLToPath } from 'url'

const __dirname = fileURLToPath(new URL('.', import.meta.url))

// Auto-discover init files
const initDir = resolve(__dirname, 'src/init')
const initFiles = readdirSync(initDir)
  .filter(file => file.endsWith('.js'))
  .reduce((acc, file) => {
    const name = file.replace('.js', '')
    acc[name] = resolve(initDir, file)
    return acc
  }, {})

// https://vite.dev/config/
export default defineConfig({
  plugins: [tailwindcss(), preact(), ],
  build: {
    outDir: "../static/dist",
    emptyOutDir: true,
    rollupOptions: {
      input: {
        ...initFiles,
        dashboard: 'src/pages/dashboard.jsx',
        crontab: 'src/pages/crontab.jsx',
        config: 'src/pages/config.jsx',
        inventory: 'src/pages/inventory.jsx',
        ansible: 'src/pages/ansible.jsx',
      },
      output: {
        entryFileNames: 'js/[name].js',
        chunkFileNames: 'js/chunks/[name].js',
        assetFileNames: (assetInfo) => {
          const name = assetInfo.name || ''
          if (name.endsWith('.css')) {
            return 'css/[name].[ext]'
          }
          return 'img/[name].[ext]'
        }
      }
    }
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
      },
      '/sync-all': {
        target: 'http://localhost:5000',
        changeOrigin: true,
      },
      '/saveContent': {
        target: 'http://localhost:5000',
        changeOrigin: true,
      },
      '/logout': {
        target: 'http://localhost:5000',
        changeOrigin: true,
      },
    },
  }
})