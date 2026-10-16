// The E2E suite exercises the built dashboard served by the real FastAPI service.
// Every run gets its own database and Git fixture; existing application data is untouched.
import { spawn, spawnSync } from 'node:child_process'
import { cpSync, mkdirSync, mkdtempSync, writeFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const root = resolve(dirname(fileURLToPath(import.meta.url)), '../..')
const virtualenvBin = resolve(root, process.platform === 'win32' ? '.venv/Scripts' : '.venv/bin')
const python = resolve(virtualenvBin, process.platform === 'win32' ? 'python.exe' : 'python')
const bundle = spawnSync(python, ['scripts/bundle_frontend.py'], { cwd: root, stdio: 'inherit' })
if (bundle.status !== 0) throw new Error('Bundling the production dashboard failed')
const stateRoot = resolve(root, '.local/e2e')
mkdirSync(stateRoot, { recursive: true })
const state = mkdtempSync(resolve(stateRoot, 'run-'))
const project = process.env.MEMGLIDE_E2E_PROJECT
  ? resolve(process.env.MEMGLIDE_E2E_PROJECT)
  : resolve(state, 'auth-repository')
if (!process.env.MEMGLIDE_E2E_PROJECT) {
  cpSync(resolve(root, 'examples/auth_repository'), project, { recursive: true })
  const git = (...args) => {
    const result = spawnSync('git', args, { cwd: project, encoding: 'utf8' })
    if (result.status !== 0) throw new Error(result.stderr || 'Git fixture setup failed')
  }
  git('init', '--quiet', '--initial-branch=main')
  git('add', '.')
  git('-c', 'user.name=Memglide E2E', '-c', 'user.email=e2e@localhost', 'commit', '--quiet', '-m', 'Authentication fixture')
}
writeFileSync(resolve(stateRoot, 'current.json'), JSON.stringify({ project, state }))
const child = spawn(resolve(virtualenvBin, process.platform === 'win32' ? 'memglide.exe' : 'memglide'), [
  '--db', resolve(state, 'memglide.db'), 'serve', '--port', process.env.MEMGLIDE_E2E_PORT ?? '8765',
], { cwd: root, env: { ...process.env, MEMGLIDE_HOME: state }, stdio: 'inherit' })
for (const signal of ['SIGTERM', 'SIGINT']) process.on(signal, () => child.kill(signal))
child.on('error', error => { console.error(error.message); process.exitCode = 1 })
child.on('exit', code => { process.exitCode = code ?? 0 })
