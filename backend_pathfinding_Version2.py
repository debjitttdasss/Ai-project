import heapq
import math

ROWS, COLS = 20, 20
VISION_RANGE = 6
VISION_FOV_DEG = 85
VISIBLE_PENALTY = 16
NEAR_VISIBLE_PENALTY = 4


def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def in_bounds(node):
    x, y = node
    return 0 <= x < ROWS and 0 <= y < COLS


def get_neighbors(node, walls):
    x, y = node
    out = []
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        nxt = (x + dx, y + dy)
        if in_bounds(nxt) and nxt not in walls:
            out.append(nxt)
    return out


def reconstruct_path(came_from, current):
    path = []
    while current in came_from:
        path.append(current)
        current = came_from[current]
    path.reverse()
    return path


def bresenham_line(a, b):
    x0, y0 = a
    x1, y1 = b
    points = []

    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy

    while True:
        points.append((x0, y0))
        if (x0, y0) == (x1, y1):
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy

    return points


def has_line_of_sight(origin, target, walls):
    line = bresenham_line(origin, target)
    for p in line[1:-1]:
        if p in walls:
            return False
    return True


def get_visible_cells(player, facing, walls, vision_range=VISION_RANGE, fov_deg=VISION_FOV_DEG):
    visible = set()
    px, py = player
    fx, fy = facing
    half = fov_deg / 2

    for x in range(ROWS):
        for y in range(COLS):
            if (x, y) == player:
                visible.add((x, y))
                continue

            dx = x - px
            dy = y - py
            dist = math.sqrt(dx * dx + dy * dy)
            if dist == 0 or dist > vision_range:
                continue

            dot = dx * fx + dy * fy
            if dot <= 0:
                continue

            angle = math.degrees(math.acos(max(-1.0, min(1.0, dot / dist))))
            if angle <= half and has_line_of_sight(player, (x, y), walls):
                visible.add((x, y))

    return visible


def expand_danger_ring(visible, walls):
    ring = set()
    for x, y in visible:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nxt = (x + dx, y + dy)
            if in_bounds(nxt) and nxt not in walls and nxt not in visible:
                ring.add(nxt)
    return ring


def build_danger_map(visible, danger_ring, goal):
    danger = {}
    for c in visible:
        danger[c] = VISIBLE_PENALTY
    for c in danger_ring:
        danger[c] = max(danger.get(c, 0), NEAR_VISIBLE_PENALTY)
    danger[goal] = 0
    return danger


def astar_safe(start, goal, walls, danger_cost):
    open_heap = []
    heapq.heappush(open_heap, (heuristic(start, goal), start))
    came_from = {}
    g_cost = {start: 0}
    seen = set()

    while open_heap:
        _, current = heapq.heappop(open_heap)
        if current in seen:
            continue
        seen.add(current)

        if current == goal:
            return reconstruct_path(came_from, current)

        for nb in get_neighbors(current, walls):
            move_cost = 1 + danger_cost.get(nb, 0)
            tg = g_cost[current] + move_cost

            if tg < g_cost.get(nb, float("inf")):
                g_cost[nb] = tg
                f = tg + heuristic(nb, goal)
                heapq.heappush(open_heap, (f, nb))
                came_from[nb] = current

    return []


def dijkstra_shortest(start, goal, walls):
    open_heap = []
    heapq.heappush(open_heap, (0, start))
    dist = {start: 0}
    came_from = {}

    while open_heap:
        d, cur = heapq.heappop(open_heap)
        if d > dist.get(cur, float("inf")):
            continue
        if cur == goal:
            return reconstruct_path(came_from, cur)

        for nb in get_neighbors(cur, walls):
            nd = d + 1
            if nd < dist.get(nb, float("inf")):
                dist[nb] = nd
                came_from[nb] = cur
                heapq.heappush(open_heap, (nd, nb))

    return []