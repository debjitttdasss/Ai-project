# Stealth Game AI (A* + Dijkstra) - Web Version

A browser-based stealth/pathfinding game using:

- **Backend:** Python + Flask
- **Frontend:** HTML/CSS/JavaScript
- **Algorithms:**  
  - Safe A* (danger-aware)  
  - Dijkstra (shortest path baseline)

## Features

- 20x20 grid
- Player movement (arrow keys)
- Player cone vision + wall line-of-sight
- Enemy route selection:
  - **SAFE A\*** mode (avoids visible + near-visible zones)
  - **DIJKSTRA** mode (shortest path only)
- Mode toggle, pause/resume, reset

## Run

```bash
pip install -r requirements.txt
python backend/app.py
```

Open: `http://127.0.0.1:5000`

## Controls

- Arrow keys: move player
- Toggle Mode button: SAFE A* / DIJKSTRA
- Pause button: pause/resume
- Reset button: restart game