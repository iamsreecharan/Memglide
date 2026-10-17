import { expect, test, type APIRequestContext, type Page } from '@playwright/test'
import { readFileSync } from 'node:fs'
import { basename, dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const mutationHeaders = { 'X-Memglide-Request': '1' }
function projectPath(): string {
  return (JSON.parse(readFileSync(resolve(dirname(fileURLToPath(import.meta.url)), '../../.local/e2e/current.json'), 'utf8')) as { project: string }).project
}
async function navigate(page: Page, name: string) {
  await page.getByRole('navigation', { name: 'Main navigation' }).getByRole('link', { name, exact: true }).click()
}
async function assertNoOverflow(page: Page) {
  expect(await page.evaluate(() => ({ document: document.documentElement.scrollWidth, viewport: window.innerWidth })))
    .toEqual({ document: (await page.viewportSize())!.width, viewport: (await page.viewportSize())!.width })
}
async function clearProjects(request: APIRequestContext) {
  const response = await request.get('/api/projects')
  expect(response.ok()).toBeTruthy()
  for (const project of await response.json() as { id: string }[]) {
    expect((await request.delete(`/api/projects/${project.id}`, { headers: mutationHeaders })).ok()).toBeTruthy()
  }
}

test('production dashboard completes the repository, session, memory, retrieval, and evidence workflow', async ({ page, request }) => {
  await clearProjects(request)
  const errors: string[] = []
  page.on('pageerror', error => errors.push(error.message))
  await page.goto('/')
  await expect(page.getByRole('heading', { name: 'Your context, in focus.' })).toBeVisible()
  await expect(page.getByText('Start with a repository', { exact: true })).toBeVisible()
  await navigate(page, 'Memory explorer')
  await expect(page.getByRole('heading', { name: 'Choose a project first' })).toBeVisible()
  await navigate(page, 'Projects')
  await page.getByRole('button', { name: 'Add repository' }).first().click()
  await page.getByLabel('Absolute repository path').fill(`${projectPath()}/missing-directory`)
  await page.getByRole('button', { name: 'Register & index' }).click()
  await expect(page.getByRole('alert')).toContainText('Request could not be completed')
  await page.getByLabel('Absolute repository path').fill(projectPath())
  await page.getByRole('button', { name: 'Register & index' }).click()
  await expect(page.getByRole('dialog')).toHaveCount(0)
  await expect(page.getByRole('heading', { name: basename(projectPath()), exact: true })).toBeVisible()
  await expect(page.getByText('main', { exact: true })).toBeVisible()
  await page.getByRole('button', { name: 'Index details' }).click()
  await expect(page.getByText('No indexing errors reported.')).toBeVisible()
  await page.getByRole('button', { name: 'Reindex', exact: true }).click()
  await expect(page.getByRole('status')).toContainText('Index updated')
  await page.getByRole('button', { name: 'New session' }).click()
  await page.getByLabel('Task', { exact: true }).fill('Investigate authentication boundaries')
  await page.getByRole('button', { name: 'Start session', exact: true }).click()
  await expect(page.getByRole('dialog')).toHaveCount(0)
  await expect(page.getByLabel('SESSION', { exact: true })).toContainText('Investigate authentication boundaries')

  await navigate(page, 'Memory explorer')
  await expect(page.getByRole('heading', { name: 'A fresh session' })).toBeVisible()
  await page.getByRole('button', { name: 'Save a memory' }).first().click()
  await page.getByLabel('Category', { exact: true }).selectOption('verified_fix')
  await page.getByLabel('Finding', { exact: true }).fill('Bearer authentication rejects an unsupported scheme before token verification.')
  await page.getByLabel('Provenance', { exact: true }).fill('Inspected authenticate_user in api/auth.py and its structural callers.')
  await page.getByLabel('Related files (optional)').fill('api/auth.py')
  await page.getByRole('button', { name: 'Save memory', exact: true }).click()
  await expect(page.getByRole('dialog')).toHaveCount(0)
  await expect(page.locator('.memory-content')).toContainText('Bearer authentication rejects')
  await expect(page.locator('.memory-provenance')).toContainText('Inspected authenticate_user')
  await expect(page.locator('.memory-sources')).toContainText('api/auth.py')
  await expect(page.locator('.memory-sources [title]')).toHaveAttribute('title', /Source hash: [a-f0-9]{64}/)
  await page.getByRole('button', { name: /^Edit memory/ }).click()
  await expect(page.getByLabel('Finding', { exact: true })).toBeFocused()
  await page.getByLabel('Finding', { exact: true }).fill('Bearer authentication validates the scheme before delegating to verify_token.')
  await page.getByRole('button', { name: 'Save changes', exact: true }).click()
  await expect(page.locator('.memory-content')).toContainText('delegating to verify_token')
  await page.getByRole('textbox', { name: 'Search memories' }).fill('nonexistent-memory-phrase')
  await expect(page.getByRole('heading', { name: 'No matching memories' })).toBeVisible()
  await page.getByRole('button', { name: 'Clear filters' }).click()
  await expect(page.locator('.memory-content')).toContainText('delegating to verify_token')

  await navigate(page, 'Context explorer')
  await page.getByLabel('WHAT DO YOU NEED TO UNDERSTAND?').fill('authenticate_user verify_token')
  await page.getByLabel('Token budget', { exact: true }).fill('12000')
  await page.getByRole('button', { name: 'Retrieve context', exact: true }).click()
  await expect(page.locator('.evidence-card').first()).toBeVisible()
  await expect(page.locator('.results-heading')).toContainText('Level 1')
  await page.getByRole('button', { name: 'Expand to level 2' }).click()
  await expect(page.locator('.results-heading')).toContainText('Level 2')
  await expect(page.locator('.code-block').first()).toContainText(/def |function /)
  await page.getByRole('button', { name: 'Expand to level 3' }).click()
  await expect(page.locator('.results-heading')).toContainText('Level 3')
  await page.getByRole('link', { name: 'View passport' }).click()
  await expect(page.getByRole('heading', { name: 'Context passport', exact: true })).toBeVisible()
  await expect(page.locator('.passport-banner')).toContainText('evidence')
  await expect(page.locator('.hash-list')).toContainText('api/auth.py')
  await expect(page.getByRole('heading', { name: 'Related tests', exact: true })).toBeVisible()
  await page.getByRole('button', { name: 'Verify source versions' }).click()
  await expect(page.locator('.passport-banner')).toContainText('Current sources')

  await navigate(page, 'Session timeline')
  await expect(page.locator('.timeline-event')).not.toHaveCount(0)
  await page.getByLabel('Event type', { exact: true }).selectOption('memory_saved')
  await expect(page.locator('.timeline-event')).toHaveCount(1)
  await expect(page.locator('.timeline-event')).toContainText('Memory Saved')
  await page.getByRole('checkbox', { name: 'Selected session only' }).check()
  await page.getByRole('button', { name: 'Event details' }).click()
  await expect(page.locator('.timeline-event .detail-json')).toBeVisible()

  await navigate(page, 'Settings')
  await page.getByLabel('Inactivity timeout (minutes)').fill('45')
  await page.getByLabel('Default context token budget').fill('6000')
  await page.getByRole('button', { name: 'Light', exact: true }).click()
  await page.getByRole('button', { name: 'Save settings' }).click()
  await expect(page.getByRole('button', { name: 'Save settings' })).toBeDisabled()
  await expect(page.locator('html')).toHaveAttribute('data-theme', 'light')
  await page.reload()
  await expect(page.getByLabel('Inactivity timeout (minutes)')).toHaveValue('45')
  await expect(page.getByLabel('Default context token budget')).toHaveValue('6000')
  await expect(page.locator('html')).toHaveAttribute('data-theme', 'light')
  await page.getByRole('button', { name: 'Dark', exact: true }).click()
  await page.getByRole('button', { name: 'Save settings' }).click()
  await expect(page.locator('html')).toHaveAttribute('data-theme', 'dark')
  await page.getByRole('button', { name: 'Run diagnostics' }).click()
  await expect(page.locator('.maintenance-panel .detail-json')).toContainText('frontend_built')
  await page.getByRole('button', { name: 'Run cleanup' }).click()
  await expect(page.getByRole('status').filter({ hasText: 'Cleanup complete' })).toBeVisible()
  await navigate(page, 'Overview')
  await expect(page.locator('.metric-value').first()).toHaveText('1')
  await page.screenshot({ path: 'test-results/memglide-overview.png', fullPage: true })
  await assertNoOverflow(page)

  await navigate(page, 'Memory explorer')
  await page.getByRole('button', { name: /^Delete memory/ }).click()
  await page.getByRole('dialog').getByRole('button', { name: 'Cancel', exact: true }).click()
  await expect(page.locator('.memory-card')).toHaveCount(1)
  await page.getByRole('button', { name: /^Delete memory/ }).click()
  await page.getByRole('dialog').getByRole('button', { name: 'Delete memory', exact: true }).click()
  await expect(page.getByRole('heading', { name: 'A fresh session' })).toBeVisible()
  await page.getByRole('button', { name: 'End selected session' }).click()
  await page.getByRole('dialog').getByRole('button', { name: 'End session', exact: true }).click()
  await expect(page.getByRole('button', { name: 'Save a memory' }).first()).toBeDisabled()
  await expect(page.getByLabel('SESSION', { exact: true })).toContainText('Investigate authentication boundaries · ended')
  await navigate(page, 'Settings')
  await page.getByRole('button', { name: 'Delete session data', exact: true }).click()
  await page.getByRole('dialog').getByRole('button', { name: 'Delete session data', exact: true }).click()
  await expect(page.getByLabel('SESSION', { exact: true })).toHaveValue('')
  await navigate(page, 'Projects')
  await page.getByRole('button', { name: `Remove ${basename(projectPath())}` }).click()
  await page.getByRole('dialog').getByRole('button', { name: 'Remove project', exact: true }).click()
  await expect(page.getByRole('heading', { name: 'Your first project starts here' })).toBeVisible()
  expect(errors).toEqual([])
})

test('background cleanup cannot redirect a session deletion confirmation to another task', async ({ page, request }) => {
  await clearProjects(request)
  const projectResponse = await request.post('/api/projects', { headers: mutationHeaders, data: { path: projectPath() } })
  expect(projectResponse.ok()).toBeTruthy()
  const project = await projectResponse.json() as { id: string }
  const sessionResponse = await request.post('/api/sessions', { headers: mutationHeaders, data: { project_id: project.id, task: 'Original deletion target' } })
  expect(sessionResponse.ok()).toBeTruthy()
  const original = await sessionResponse.json() as { id: string }
  const remainingResponse = await request.post('/api/sessions', { headers: mutationHeaders, data: { project_id: project.id, task: 'Keep this task' } })
  expect(remainingResponse.ok()).toBeTruthy()
  const remaining = await remainingResponse.json() as { id: string }
  await page.clock.install()
  await page.goto('/memory')
  await page.getByLabel('SESSION', { exact: true }).selectOption(original.id)
  await expect(page.getByLabel('SESSION', { exact: true })).toHaveValue(original.id)
  await page.getByRole('button', { name: 'Delete selected session and memory' }).click()
  await expect(page.getByRole('dialog')).toContainText('Original deletion target')
  expect((await request.post(`/api/sessions/${original.id}/clear`, { headers: mutationHeaders })).ok()).toBeTruthy()
  // Advance the normal polling interval, preserving the real request/response
  // path and avoiding a wall-clock sleep in the production browser test.
  await page.clock.fastForward(15_001)
  await expect(page.getByLabel('SESSION', { exact: true })).toHaveValue(remaining.id)
  await page.getByRole('dialog').getByRole('button', { name: 'Delete session', exact: true }).click()
  await expect(page.getByRole('dialog').getByRole('alert')).toContainText('Request could not be completed')
  const sessionsResponse = await request.get(`/api/sessions?project_id=${project.id}`)
  expect(sessionsResponse.ok()).toBeTruthy()
  expect((await sessionsResponse.json() as { id: string }[]).map(item => item.id)).toEqual([remaining.id])
  await expect(page.getByLabel('SESSION', { exact: true })).toHaveValue(remaining.id)
})

test('production routes retain useful empty and error states and fit desktop and tablet', async ({ page, request }) => {
  await clearProjects(request)
  const errors: string[] = []
  page.on('pageerror', error => errors.push(error.message))
  await page.goto('/passport')
  await expect(page.getByRole('heading', { name: 'Every retrieval gets a passport' })).toBeVisible()
  const projectResponse = await request.post('/api/projects', { headers: mutationHeaders, data: { path: projectPath() } })
  expect(projectResponse.ok()).toBeTruthy()
  const project = await projectResponse.json() as { id: string }
  const sessionResponse = await request.post('/api/sessions', { headers: mutationHeaders, data: { project_id: project.id, task: 'Review production dashboard responsiveness' } })
  expect(sessionResponse.ok()).toBeTruthy()
  const session = await sessionResponse.json() as { id: string }
  const anotherSessionResponse = await request.post('/api/sessions', { headers: mutationHeaders, data: { project_id: project.id, task: 'Compare active task workspaces' } })
  expect(anotherSessionResponse.ok()).toBeTruthy()
  const anotherSession = await anotherSessionResponse.json() as { id: string }
  await page.goto(`/passport?retrieval=missing-retrieval&session=${session.id}`)
  await expect(page.getByLabel('SESSION', { exact: true })).toHaveValue(session.id)
  await expect(page.getByRole('alert')).toContainText('Request could not be completed')
  await expect(page.getByRole('button', { name: 'Try again' })).toBeVisible()
  await page.goto('/context')
  await page.getByLabel('SESSION', { exact: true }).selectOption(anotherSession.id)
  await expect(page.getByLabel('SESSION', { exact: true })).toHaveValue(anotherSession.id)
  await page.getByLabel('SESSION', { exact: true }).selectOption(session.id)
  await expect(page.getByLabel('SESSION', { exact: true })).toHaveValue(session.id)
  await page.getByLabel('WHAT DO YOU NEED TO UNDERSTAND?').fill('zxqvnonexistent934712')
  await expect(page.getByRole('button', { name: 'Retrieve context', exact: true })).toBeEnabled()
  await page.getByRole('button', { name: 'Retrieve context', exact: true }).click()
  await expect(page.getByRole('heading', { name: 'No source evidence matched' })).toBeVisible()
  const routes = [
    ['/', 'Your context, in focus.'], ['/projects', 'Projects'], ['/memory', 'Memory explorer'],
    ['/context', 'Context explorer'], ['/passport', 'Context passport'], ['/timeline', 'Session timeline'], ['/settings', 'Settings'],
  ] as const
  for (const width of [1440, 1024, 768]) {
    await page.setViewportSize({ width, height: 1000 })
    for (const [path, heading] of routes) {
      await page.goto(path)
      await expect(page.getByRole('heading', { name: heading, exact: true })).toBeVisible()
      await expect(page.getByText('Localhost', { exact: true })).toBeVisible()
      await assertNoOverflow(page)
    }
  }
  await page.goto('/')
  await page.screenshot({ path: 'test-results/memglide-tablet.png', fullPage: true })
  expect(errors).toEqual([])
})
