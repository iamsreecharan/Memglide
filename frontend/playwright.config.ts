import { defineConfig } from '@playwright/test'
import { existsSync, mkdirSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const frontend = dirname(fileURLToPath(import.meta.url))
const browserState = resolve(frontend, '../.local/e2e/browser')
for (const directory of ['tmp', 'cache', 'config']) mkdirSync(resolve(browserState, directory), { recursive: true })
const executablePath = process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH
  ?? (existsSync('/usr/bin/chromium') ? '/usr/bin/chromium' : undefined)
const port = Number(process.env.MEMGLIDE_E2E_PORT ?? 8765)

export default defineConfig({
  testDir: './e2e',
  fullyParallel: false,
  workers: 1,
  retries: 0,
  timeout: 90_000,
  expect: { timeout: 10_000 },
  reporter: [['list'], ['html', { open: 'never' }]],
  outputDir: './test-results',
  use: {
    baseURL: `http://127.0.0.1:${port}`,
    browserName: 'chromium',
    viewport: { width: 1440, height: 1000 },
    launchOptions: {
      executablePath,
      env: {
        ...process.env,
        TMPDIR: resolve(browserState, 'tmp'),
        XDG_CACHE_HOME: resolve(browserState, 'cache'),
        XDG_CONFIG_HOME: resolve(browserState, 'config'),
      },
    },
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
  },
  webServer: {
    command: 'npm run build && node e2e/server.mjs',
    cwd: frontend,
    url: `http://127.0.0.1:${port}/api/health`,
    timeout: 120_000,
    reuseExistingServer: false,
    gracefulShutdown: { signal: 'SIGTERM', timeout: 5000 },
  },
})
