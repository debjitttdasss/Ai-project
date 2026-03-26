from pathfinding import (
    ROWS, COLS,
    get_visible_cells, expand_danger_ring, build_danger_map,
    astar_safe, dijkstra_shortest
)

ENEMY_MOVE_INTERVAL_MS = 420


def generate_walls():
    walls = set()

    for x in range(4, 16):
        if x not in (8, 12):
            walls.add((x, 8))
    for y in range(9, 17):
        if y not in (11, 14):
            walls.add((12, y))
    for x in range(2, 11):
        if x != 6:
            walls.add((x, 15))

    return walls


class GameState:
    def __init__(self):
        self.rows = ROWS
        self.cols = COLS
        self.walls = generate_walls()
        self.player = (15, 17)
        self.enemy = (2, 2)
        self.facing = (-1, 0)
        self.use_safe_mode = True
        self.paused = False
        self.game_over = False
        self.last_enemy_move = 0

        self.walls.discard(self.player)
        self.walls.discard(self.enemy)

    def to_json(self, now_ms):
        visible = get_visible_cells(self.player, self.facing, self.walls)
        danger_ring = expand_danger_ring(visible, self.walls)
        danger_cost = build_danger_map(visible, danger_ring, self.player)

        shortest_path = dijkstra_shortest(self.enemy, self.player, self.walls)
        safe_path = astar_safe(self.enemy, self.player, self.walls, danger_cost)

        active_path = safe_path if self.use_safe_mode else shortest_path
        if not self.paused and not self.game_over:
            if active_path and now_ms - self.last_enemy_move >= ENEMY_MOVE_INTERVAL_MS:
                self.enemy = active_path[0]
                self.last_enemy_move = now_ms

        if self.enemy == self.player:
            self.game_over = True

        return {
            "rows": self.rows,
            "cols": self.cols,
            "walls": [list(x) for x in self.walls],
            "player": list(self.player),
            "enemy": list(self.enemy),
            "facing": list(self.facing),
            "visible": [list(x) for x in visible],
            "danger_ring": [list(x) for x in danger_ring],
            "safe_path": [list(x) for x in safe_path],
            "shortest_path": [list(x) for x in shortest_path],
            "mode": "SAFE_ASTAR" if self.use_safe_mode else "DIJKSTRA",
            "paused": self.paused,
            "game_over": self.game_over
        }

    def move_player(self, direction):
        if self.game_over:
            return

        x, y = self.player
        next_pos = self.player
        next_facing = self.facing

        if direction == "UP":
            next_pos = (x - 1, y)
            next_facing = (-1, 0)
        elif direction == "DOWN":
            next_pos = (x + 1, y)
            next_facing = (1, 0)
        elif direction == "LEFT":
            next_pos = (x, y - 1)
            next_facing = (0, -1)
        elif direction == "RIGHT":
            next_pos = (x, y + 1)
            next_facing = (0, 1)

        if (0 <= next_pos[0] < self.rows and
                0 <= next_pos[1] < self.cols and
                next_pos not in self.walls):
            self.player = next_pos

        self.facing = next_facing

    def toggle_mode(self):
        self.use_safe_mode = not self.use_safe_mode

    def toggle_pause(self):
        self.paused = not self.paused

    def reset(self):
        self.__init__()