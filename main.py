"""
Snake AI — Main
===============
Author  : [Perrine , Gaelle]
Project : AI Search Algorithms — Snake with A*

Controls
--------
SPACE  : pause / resume
F      : toggle fast mode
P      : toggle path preview
R      : restart
ESC    : quit
"""

import sys
import pygame

from config  import *
from snake   import Snake, Food
from astar   import astar


# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────
def cell_to_px(row, col):
    """Convert grid cell to pixel top-left corner."""
    x = col * CELL_SIZE
    y = PANEL_HEIGHT + row * CELL_SIZE
    return x, y


def draw_rounded_rect(surface, color, rect, radius=6):
    pygame.draw.rect(surface, color, rect, border_radius=radius)


# ─────────────────────────────────────────────
#  DRAW FUNCTIONS
# ─────────────────────────────────────────────
def draw_grid(surface):
    for r in range(GRID_ROWS + 1):
        y = PANEL_HEIGHT + r * CELL_SIZE
        pygame.draw.line(surface, GRID_COLOR, (0, y), (WINDOW_WIDTH, y))
    for c in range(GRID_COLS + 1):
        x = c * CELL_SIZE
        pygame.draw.line(surface, GRID_COLOR, (x, PANEL_HEIGHT), (x, WINDOW_HEIGHT))


def draw_path_preview(surface, path, explored):
    """Draw explored cells and planned path (faint overlay)."""
    for cell in explored:
        r, c = cell
        x, y = cell_to_px(r, c)
        s = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        s.fill((*EXPLORE_COL, 60))
        surface.blit(s, (x, y))

    for cell in path:
        r, c = cell
        x, y = cell_to_px(r, c)
        s = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        s.fill((*PATH_COLOR, 100))
        surface.blit(s, (x, y))
        # dot in center
        cx, cy = x + CELL_SIZE // 2, y + CELL_SIZE // 2
        pygame.draw.circle(surface, PATH_COLOR, (cx, cy), 4)


def draw_food(surface, food, tick):
    r, c = food.position
    x, y = cell_to_px(r, c)
    cx   = x + CELL_SIZE // 2
    cy   = y + CELL_SIZE // 2
    # pulsing glow
    glow_r = int(8 + 4 * abs((tick % 30) - 15) / 15)
    pygame.draw.circle(surface, FOOD_GLOW, (cx, cy), glow_r + 4)
    pygame.draw.circle(surface, FOOD_COLOR, (cx, cy), glow_r)


def draw_snake(surface, snake):
    for i, (r, c) in enumerate(snake.body):
        x, y = cell_to_px(r, c)
        rect = pygame.Rect(x + 1, y + 1, CELL_SIZE - 2, CELL_SIZE - 2)
        if i == 0:
            draw_rounded_rect(surface, SNAKE_HEAD, rect, radius=8)
            # eyes
            ex1 = x + CELL_SIZE // 3
            ex2 = x + 2 * CELL_SIZE // 3
            ey  = y + CELL_SIZE // 3
            pygame.draw.circle(surface, EYE_COLOR, (ex1, ey), 3)
            pygame.draw.circle(surface, EYE_COLOR, (ex2, ey), 3)
        elif i == len(snake.body) - 1:
            draw_rounded_rect(surface, SNAKE_DARK, rect, radius=6)
        else:
            draw_rounded_rect(surface, SNAKE_BODY, rect, radius=4)


def draw_panel(surface, font, score, high_score, nodes_explored, path_len, paused, fast, show_path):
    pygame.draw.rect(surface, PANEL_COLOR, (0, 0, WINDOW_WIDTH, PANEL_HEIGHT))
    pygame.draw.line(surface, GRID_COLOR, (0, PANEL_HEIGHT), (WINDOW_WIDTH, PANEL_HEIGHT), 2)

    # Score
    s1 = font.render(f"Score: {score}", True, GOLD)
    s2 = font.render(f"Best: {high_score}", True, TEXT_COLOR)
    s3 = font.render(f"Nodes: {nodes_explored}", True, ACCENT)
    s4 = font.render(f"Path: {path_len}", True, ACCENT)

    surface.blit(s1, (10, 10))
    surface.blit(s2, (10, 32))
    surface.blit(s3, (200, 10))
    surface.blit(s4, (200, 32))

    # Flags
    flags = []
    if paused:     flags.append("PAUSED")
    if fast:       flags.append("FAST")
    if show_path:  flags.append("PATH")
    if flags:
        sf = font.render("  ".join(flags), True, (180, 180, 100))
        surface.blit(sf, (420, 20))

    # Controls hint
    hint = font.render("SPACE:pause  F:fast  P:path  R:reset  ESC:quit", True, (80, 80, 100))
    surface.blit(hint, (WINDOW_WIDTH - hint.get_width() - 5, PANEL_HEIGHT - 18))


def draw_game_over(surface, font_big, font, score):
    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    surface.blit(overlay, (0, 0))

    t1 = font_big.render("GAME OVER", True, FOOD_COLOR)
    t2 = font.render(f"Score: {score}", True, GOLD)
    t3 = font.render("Press R to restart or ESC to quit", True, TEXT_COLOR)

    surface.blit(t1, (WINDOW_WIDTH // 2 - t1.get_width() // 2, WINDOW_HEIGHT // 2 - 60))
    surface.blit(t2, (WINDOW_WIDTH // 2 - t2.get_width() // 2, WINDOW_HEIGHT // 2))
    surface.blit(t3, (WINDOW_WIDTH // 2 - t3.get_width() // 2, WINDOW_HEIGHT // 2 + 40))


# ─────────────────────────────────────────────
#  FALLBACK DIRECTION (when A* finds no path)
# ─────────────────────────────────────────────
def fallback_direction(snake):
    """Try any safe direction to keep the snake alive."""
    r, c    = snake.head
    body_s  = snake.obstacles
    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nr, nc = r + dr, c + dc
        if 0 <= nr < GRID_ROWS and 0 <= nc < GRID_COLS and (nr, nc) not in body_s:
            return (dr, dc)
    return snake.direction   # no safe move → die


# ─────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────
def main():
    pygame.init()
    screen  = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Snake AI — A* Pathfinding")
    clock   = pygame.time.Clock()

    font     = pygame.font.SysFont("consolas", 14)
    font_big = pygame.font.SysFont("consolas", 42, bold=True)

    # ── Game state ────────────────────────────
    snake       = Snake()
    food        = Food(snake.body)
    score       = 0
    high_score  = 0
    tick        = 0

    paused      = False
    fast_mode   = False
    show_path   = True
    game_over   = False

    current_path     = []
    explored_cells   = set()
    nodes_explored   = 0

    # Compute initial path
    current_path, explored_cells = astar(snake.head, food.position, snake.obstacles)
    nodes_explored = len(explored_cells)

    # ── Main loop ─────────────────────────────
    while True:
        speed = SPEED_FAST if fast_mode else SPEED_NORMAL

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()
                if event.key == pygame.K_SPACE:
                    paused = not paused
                if event.key == pygame.K_f:
                    fast_mode = not fast_mode
                if event.key == pygame.K_p:
                    show_path = not show_path
                if event.key == pygame.K_r:
                    snake      = Snake()
                    food       = Food(snake.body)
                    score      = 0
                    game_over  = False
                    tick       = 0
                    current_path, explored_cells = astar(snake.head, food.position, snake.obstacles)
                    nodes_explored = len(explored_cells)

        if not paused and not game_over:
            # ── AI decision ───────────────────
            if current_path:
                next_cell   = current_path[0]
                dr          = next_cell[0] - snake.head[0]
                dc          = next_cell[1] - snake.head[1]
                snake.direction = (dr, dc)
                current_path    = current_path[1:]
            else:
                # No path → try fallback
                snake.direction = fallback_direction(snake)

            snake.move()
            tick += 1

            if not snake.alive:
                game_over  = True
                high_score = max(high_score, score)
                continue

            # ── Food eaten ────────────────────
            if snake.head == food.position:
                snake.grow()
                score += 1
                food.respawn(snake.body)
                current_path, explored_cells = astar(snake.head, food.position, snake.obstacles)
                nodes_explored = len(explored_cells)

            # ── Recompute path if empty ────────
            elif not current_path:
                current_path, explored_cells = astar(snake.head, food.position, snake.obstacles)
                nodes_explored = len(explored_cells)

        # ── Render ────────────────────────────
        screen.fill(DARK_BG)
        draw_grid(screen)

        if show_path and not game_over:
            draw_path_preview(screen, current_path, explored_cells)

        draw_food(screen, food, tick)
        draw_snake(screen, snake)
        draw_panel(screen, font, score, high_score, nodes_explored, len(current_path), paused, fast_mode, show_path)

        if game_over:
            draw_game_over(screen, font_big, font, score)

        pygame.display.flip()
        clock.tick(1000 // speed)


if __name__ == "__main__":
    main()
