'use strict';

const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');
const statusEl = document.getElementById('status');
const modeBtn = document.getElementById('modeBtn');
const pauseBtn = document.getElementById('pauseBtn');
const resetBtn = document.getElementById('resetBtn');

// Grid is 20x20, canvas is 600x600
const CELL = 30;

// Rendering colours (matching CSS custom properties)
const COLORS = {
  bg: '#f8fafc',
  grid: '#e2e8f0',
  wall: '#334155',
  visible: '#fef08a',
  nearDanger: '#fef9c3',
  safePath: '#22c55e',
  dijkstraPath: '#94a3b8',
  player: '#3b82f6',
  playerStroke: '#1d4ed8',
  enemy: '#ef4444',
  enemyStroke: '#b91c1c',
};

let gameState = null;

// ─── Rendering ────────────────────────────────────────────────────────────────

function cellXY(row, col) {
  return { x: col * CELL, y: row * CELL };
}

function drawCircle(row, col, fill, stroke) {
  const { x, y } = cellXY(row, col);
  const cx = x + CELL / 2;
  const cy = y + CELL / 2;
  const r = CELL / 2 - 3;
  ctx.beginPath();
  ctx.arc(cx, cy, r, 0, Math.PI * 2);
  ctx.fillStyle = fill;
  ctx.fill();
  ctx.strokeStyle = stroke;
  ctx.lineWidth = 2;
  ctx.stroke();
}

function render() {
  if (!gameState) return;

  const {
    rows, cols, walls,
    player, enemy,
    visible, danger_ring,
    safe_path, shortest_path,
    game_over,
  } = gameState;

  // Background
  ctx.fillStyle = COLORS.bg;
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  // Index sets for quick membership tests
  const visibleSet = new Set(visible.map(([r, c]) => `${r},${c}`));

  // Near-danger cells (danger ring)
  for (const [r, c] of danger_ring) {
    if (!visibleSet.has(`${r},${c}`)) {
      const { x, y } = cellXY(r, c);
      ctx.fillStyle = COLORS.nearDanger;
      ctx.fillRect(x, y, CELL, CELL);
    }
  }

  // Visible / danger cells
  for (const [r, c] of visible) {
    const { x, y } = cellXY(r, c);
    ctx.fillStyle = COLORS.visible;
    ctx.fillRect(x, y, CELL, CELL);
  }

  // Dijkstra path dots (drawn behind safe path)
  for (const [r, c] of shortest_path) {
    const { x, y } = cellXY(r, c);
    ctx.fillStyle = COLORS.dijkstraPath;
    ctx.fillRect(x + 8, y + 8, CELL - 16, CELL - 16);
  }

  // Safe A* path dots (drawn on top)
  for (const [r, c] of safe_path) {
    const { x, y } = cellXY(r, c);
    ctx.fillStyle = COLORS.safePath;
    ctx.fillRect(x + 8, y + 8, CELL - 16, CELL - 16);
  }

  // Walls
  for (const [r, c] of walls) {
    const { x, y } = cellXY(r, c);
    ctx.fillStyle = COLORS.wall;
    ctx.fillRect(x, y, CELL, CELL);
  }

  // Grid lines
  ctx.strokeStyle = COLORS.grid;
  ctx.lineWidth = 0.5;
  for (let r = 0; r <= rows; r++) {
    ctx.beginPath();
    ctx.moveTo(0, r * CELL);
    ctx.lineTo(cols * CELL, r * CELL);
    ctx.stroke();
  }
  for (let c = 0; c <= cols; c++) {
    ctx.beginPath();
    ctx.moveTo(c * CELL, 0);
    ctx.lineTo(c * CELL, rows * CELL);
    ctx.stroke();
  }

  // Enemy
  drawCircle(enemy[0], enemy[1], COLORS.enemy, COLORS.enemyStroke);

  // Player (drawn last so it's always on top)
  drawCircle(player[0], player[1], COLORS.player, COLORS.playerStroke);

  // Game-over overlay
  if (game_over) {
    ctx.fillStyle = 'rgba(0,0,0,0.55)';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = '#ffffff';
    ctx.font = 'bold 36px Inter, Arial, sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText('GAME OVER', canvas.width / 2, canvas.height / 2 - 22);
    ctx.font = '18px Inter, Arial, sans-serif';
    ctx.fillText('Press Reset to play again', canvas.width / 2, canvas.height / 2 + 22);
  }
}

// ─── Status badge ─────────────────────────────────────────────────────────────

function updateStatus() {
  if (!gameState) return;

  if (gameState.game_over) {
    statusEl.textContent = 'Game Over';
    statusEl.style.background = '#fee2e2';
    statusEl.style.color = '#991b1b';
  } else if (gameState.paused) {
    statusEl.textContent = 'Paused';
    statusEl.style.background = '#fef9c3';
    statusEl.style.color = '#854d0e';
  } else {
    statusEl.textContent = gameState.mode === 'SAFE_ASTAR' ? 'Safe A*' : 'Dijkstra';
    statusEl.style.background = '#dcfce7';
    statusEl.style.color = '#166534';
  }
}

// ─── API helpers ──────────────────────────────────────────────────────────────

async function apiFetch(path, options) {
  try {
    const res = await fetch(path, options);
    if (!res.ok) {
      console.error(`API error ${res.status} for ${path}`);
    }
    return res;
  } catch (err) {
    console.error(`Network error for ${path}:`, err);
    return null;
  }
}

async function fetchState() {
  const res = await apiFetch('/api/state');
  if (!res) return;
  try {
    gameState = await res.json();
    render();
    updateStatus();
  } catch (err) {
    console.error('Failed to parse game state:', err);
  }
}

// ─── Game loop ────────────────────────────────────────────────────────────────

const POLL_INTERVAL_MS = 150;

function scheduleNextPoll() {
  setTimeout(async () => {
    await fetchState();
    scheduleNextPoll();
  }, POLL_INTERVAL_MS);
}

// ─── Keyboard input ───────────────────────────────────────────────────────────

const KEY_TO_DIR = {
  ArrowUp: 'UP',
  ArrowDown: 'DOWN',
  ArrowLeft: 'LEFT',
  ArrowRight: 'RIGHT',
};

document.addEventListener('keydown', async (e) => {
  const dir = KEY_TO_DIR[e.key];
  if (!dir) return;
  e.preventDefault();

  const res = await apiFetch('/api/move', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ direction: dir }),
  });
  if (res) await fetchState();
});

// ─── Button handlers ──────────────────────────────────────────────────────────

modeBtn.addEventListener('click', async () => {
  const res = await apiFetch('/api/toggle-mode', { method: 'POST' });
  if (res) await fetchState();
});

pauseBtn.addEventListener('click', async () => {
  const res = await apiFetch('/api/toggle-pause', { method: 'POST' });
  if (res) await fetchState();
});

resetBtn.addEventListener('click', async () => {
  const res = await apiFetch('/api/reset', { method: 'POST' });
  if (res) await fetchState();
});

// ─── Bootstrap ────────────────────────────────────────────────────────────────

fetchState();
scheduleNextPoll();
