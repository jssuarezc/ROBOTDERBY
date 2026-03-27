const API    = 'http://localhost:8000'
const CELL   = 20
const COLORS = {
  wall:  '#2a2840',
  path:  '#0f0f12',
  goal:  '#1D9E75',
  start: '#534AB7',
}

const canvas = document.getElementById('canvas')
const ctx    = canvas.getContext('2d')
let state    = null
let running  = false
let timer    = null

function drawMaze(maze) {
  canvas.width  = maze.width  * CELL
  canvas.height = maze.height * CELL

  maze.grid.forEach((row, r) => {
    row.forEach((cell, c) => {
      ctx.fillStyle = cell === 1 ? COLORS.wall : COLORS.path
      ctx.fillRect(c * CELL, r * CELL, CELL, CELL)
    })
  })

  const [sr, sc] = maze.start
  const [gr, gc] = maze.goal
  ctx.fillStyle = COLORS.start
  ctx.fillRect(sc * CELL, sr * CELL, CELL, CELL)
  ctx.fillStyle = COLORS.goal
  ctx.fillRect(gc * CELL, gr * CELL, CELL, CELL)
}

function drawAgents(agents) {
  const offsets = [[4, 4], [4, 12], [12, 4]]
  agents.forEach((agent, i) => {
    const [r, c] = agent.position
    const [ox, oy] = offsets[i]
    ctx.fillStyle = agent.color
    ctx.fillRect(c * CELL + ox, r * CELL + oy, CELL - 12, CELL - 12)
  })
}

function render(data) {
  drawMaze(data.maze)
  drawAgents(data.agents)
  updateCards(data.agents)
}

function updateCards(agents) {
  const container = document.getElementById('agent-cards')
  container.innerHTML = agents.map(a => {
    const status = a.done
      ? `<span class="badge" style="background:#0a1f18;color:#5DCAA5">done</span>`
      : `<span class="badge" style="background:#1a1a22;color:#888">racing</span>`
    return `
      <div class="agent-card">
        <div class="agent-name" style="color:${a.color}">${a.name}</div>
        <div class="agent-row"><span>Steps</span><span>${a.steps}</span></div>
        <div class="agent-row"><span>Wins</span><span>${a.wins}</span></div>
        <div class="agent-row"><span>Status</span>${status}</div>
      </div>`
  }).join('')
}

async function tick() {
  const res  = await fetch(`${API}/step`, { method: 'POST' })
  const data = await res.json()
  console.log(data)
  render(data)
  if (data.done) stop()
}

function getInterval() {
  const v = +document.getElementById('speed').value
  return Math.round(500 / v)
}

function start() {
  if (running) return
  running = true
  document.getElementById('btn-run').textContent = 'Pause'
  timer = setInterval(tick, getInterval())
}

function stop() {
  running = false
  document.getElementById('btn-run').textContent = 'Run'
  clearInterval(timer)
}

document.getElementById('btn-run').addEventListener('click', () => {
  running ? stop() : start()
})

document.getElementById('btn-reset').addEventListener('click', async () => {
  stop()
  const res  = await fetch(`${API}/reset`, { method: 'POST' })
  const data = await res.json()
  render(data)
})

document.getElementById('speed').addEventListener('input', (e) => {
  document.getElementById('speed-label').textContent = e.target.value + '×'
  if (running) { stop(); start() }
})

fetch(`${API}/maze`)
  .then(r => r.json())
  .then(data => render(data))