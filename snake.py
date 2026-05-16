"""
Snake — game logic (no rendering here).
"""

import random
from config import GRID_ROWS, GRID_COLS


class Snake:
    def __init__(self):
        self.reset()

    def reset(self):
        # Start in the middle, length 3 
        mid_r = GRID_ROWS // 2
        mid_c = GRID_COLS // 2
        self.body      = [(mid_r, mid_c), (mid_r, mid_c + 1), (mid_r, mid_c + 2)]
        self.direction = (0, -1)   # moving left
        self.alive     = True
        self.grew      = False

    # ── head ──────────────────────────────────
    @property
    def head(self):
        return self.body[0]

    # ── body as set (for fast collision check) ─
    @property
    def body_set(self):
        return set(self.body)

    # ── obstacles = body without tail ─────────
    #  (tail will move away, so it's safe to enter)
    @property
    def obstacles(self):
        if self.grew:
            return set(self.body)          # tail stays → block it
        return set(self.body[:-1])         # tail leaves → allow it

    # ── move ──────────────────────────────────
    def move(self, direction=None):
        if direction:
            self.direction = direction

        dr, dc   = self.direction
        new_head = (self.head[0] + dr, self.head[1] + dc)

        # Wall collision
        if not (0 <= new_head[0] < GRID_ROWS and 0 <= new_head[1] < GRID_COLS):
            self.alive = False
            return

        # Self collision
        if new_head in set(self.body[:-1]):
            self.alive = False
            return

        self.body.insert(0, new_head)
        if not self.grew:
            self.body.pop()
        self.grew = False

    def grow(self):
        self.grew = True


class Food:
    def __init__(self, snake_body):
        self.position = self._random_pos(snake_body)

    def _random_pos(self, snake_body):
        body_set = set(snake_body)
        all_cells = [
            (r, c)
            for r in range(GRID_ROWS)
            for c in range(GRID_COLS)
            if (r, c) not in body_set
        ]
        return random.choice(all_cells)

    def respawn(self, snake_body):
        self.position = self._random_pos(snake_body)
