import pygame
import random
import heapq
import math
import sys

pygame.init()

# =========================
# CONFIGURATION
# =========================

TILE = 28
FPS = 60

MAZE = [
    "#####################",
    "#.........#.........#",
    "#.###.####.#.####.###.#",
    "#o###.####.#.####.###o#",
    "#.....................#",
    "#.###.#.#######.#.###.#",
    "#.....#...###...#.....#",
    "#####.### ### ###.#####",
    "    #.#       #.#    ",
    "#####.# ## ## #.#####",
    "     .  #   #  .     ",
    "#####.# ## ## #.#####",
    "    #.#       #.#    ",
    "#####.### ### ###.#####",
    "#.....#...###...#.....#",
    "#.###.#.#######.#.###.#",
    "#.....................#",
    "#o###.####.#.####.###o#",
    "#.###.####.#.####.###.#",
    "#.........#.........#",
    "#####################"
]

# Fix maze width by padding spaces
MAX_WIDTH = max(len(row) for row in MAZE)

MAZE = [row.ljust(MAX_WIDTH) for row in MAZE]

ROWS = len(MAZE)
COLS = MAX_WIDTH

WIDTH = COLS * TILE
HEIGHT = ROWS * TILE + 70

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AI Pac-Man - A* Intelligence")

clock = pygame.time.Clock()

FONT = pygame.font.SysFont("Arial", 24, bold=True)
BIG_FONT = pygame.font.SysFont("Arial", 48, bold=True)
SMALL_FONT = pygame.font.SysFont("Arial", 18, bold=True)


# =========================
# COLORS
# =========================

BLACK = (5, 5, 15)
BLUE = (20, 50, 200)
LIGHT_BLUE = (60, 100, 255)
YELLOW = (255, 220, 0)
WHITE = (255, 255, 255)
RED = (230, 40, 40)
PINK = (255, 120, 180)
CYAN = (40, 220, 220)
ORANGE = (255, 150, 40)
GREEN = (40, 220, 80)
DARK_RED = (150, 20, 20)
FRIGHTENED = (50, 70, 255)


# =========================
# DIRECTIONS
# =========================

DIRS = {
    "UP": (0, -1),
    "DOWN": (0, 1),
    "LEFT": (-1, 0),
    "RIGHT": (1, 0)
}

KEY_DIRS = {
    pygame.K_UP: "UP",
    pygame.K_DOWN: "DOWN",
    pygame.K_LEFT: "LEFT",
    pygame.K_RIGHT: "RIGHT",
    pygame.K_w: "UP",
    pygame.K_s: "DOWN",
    pygame.K_a: "LEFT",
    pygame.K_d: "RIGHT"
}


# =========================
# HELPER FUNCTIONS
# =========================

def grid_to_pixel(pos):
    x, y = pos
    return (
        x * TILE + TILE // 2,
        y * TILE + TILE // 2
    )


def is_wall(x, y):
    if y < 0 or y >= ROWS:
        return True

    if x < 0 or x >= COLS:
        return True

    return MAZE[y][x] == "#"


def valid_neighbors(pos):
    x, y = pos

    for dx, dy in DIRS.values():
        nx = x + dx
        ny = y + dy

        if not is_wall(nx, ny):
            yield (nx, ny)


def manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


# =========================
# A* PATHFINDING
# =========================

def astar(start, goal):
    if start == goal:
        return [start]

    open_set = []
    heapq.heappush(open_set, (0, start))

    came_from = {}

    g_score = {
        start: 0
    }

    f_score = {
        start: manhattan(start, goal)
    }

    visited = set()

    while open_set:

        _, current = heapq.heappop(open_set)

        if current in visited:
            continue

        visited.add(current)

        if current == goal:

            path = []

            while current in came_from:
                path.append(current)
                current = came_from[current]

            path.append(start)
            path.reverse()

            return path

        for neighbor in valid_neighbors(current):

            tentative_g = g_score[current] + 1

            if tentative_g < g_score.get(neighbor, float("inf")):

                came_from[neighbor] = current

                g_score[neighbor] = tentative_g

                f = tentative_g + manhattan(
                    neighbor,
                    goal
                )

                f_score[neighbor] = f

                heapq.heappush(
                    open_set,
                    (f, neighbor)
                )

    return []


# =========================
# PACMAN
# =========================

class Pacman:

    def __init__(self):

        self.start_pos = (10, 16)

        self.pos = self.start_pos

        self.direction = "LEFT"

        self.next_direction = "LEFT"

        self.moving = True

        self.anim = 0

    def reset(self):

        self.pos = self.start_pos
        self.direction = "LEFT"
        self.next_direction = "LEFT"

    def can_move(self, direction):

        dx, dy = DIRS[direction]

        nx = (self.pos[0] + dx) % COLS
        ny = (self.pos[1] + dy) % ROWS

        return not is_wall(nx, ny)

    def update(self):

        if self.can_move(self.next_direction):

            self.direction = self.next_direction

        if self.can_move(self.direction):

            dx, dy = DIRS[self.direction]

            self.pos = (
                (self.pos[0] + dx) % COLS,
                (self.pos[1] + dy) % ROWS
            )

    def draw(self):

        x, y = grid_to_pixel(self.pos)

        mouth = abs(math.sin(self.anim)) * 0.35

        start_angle = 0
        end_angle = math.pi * 2

        if self.direction == "RIGHT":

            start_angle = mouth
            end_angle = 2 * math.pi - mouth

        elif self.direction == "LEFT":

            start_angle = math.pi + mouth
            end_angle = math.pi - mouth

        elif self.direction == "UP":

            start_angle = 1.5 * math.pi + mouth
            end_angle = 1.5 * math.pi - mouth

        elif self.direction == "DOWN":

            start_angle = 0.5 * math.pi + mouth
            end_angle = 0.5 * math.pi - mouth

        pygame.draw.circle(
            screen,
            YELLOW,
            (x, y),
            TILE // 2 - 2
        )

        # Mouth
        if mouth > 0.05:

            points = [
                (x, y),
                (
                    x + math.cos(start_angle) * TILE,
                    y + math.sin(start_angle) * TILE
                ),
                (
                    x + math.cos(end_angle) * TILE,
                    y + math.sin(end_angle) * TILE
                )
            ]

            pygame.draw.polygon(
                screen,
                BLACK,
                points
            )


# =========================
# GHOST
# =========================

class Ghost:

    def __init__(self, pos, color, name, behavior):

        self.start_pos = pos

        self.pos = pos

        self.color = color

        self.name = name

        self.behavior = behavior

        self.path = []

        self.frightened = False

        self.dead = False

        self.repath_timer = 0

    def reset(self):

        self.pos = self.start_pos

        self.frightened = False

        self.dead = False

        self.path = []

        self.repath_timer = 0

    def choose_target(self, pacman):

        if self.behavior == "CHASE":

            return pacman.pos

        if self.behavior == "AMBUSH":

            dx, dy = DIRS[pacman.direction]

            return (
                pacman.pos[0] + dx * 4,
                pacman.pos[1] + dy * 4
            )

        if self.behavior == "RANDOM":

            possible = list(valid_neighbors(pacman.pos))

            if possible:

                return random.choice(possible)

            return pacman.pos

        if self.behavior == "SMART":

            distance = manhattan(
                self.pos,
                pacman.pos
            )

            if distance < 8:

                return pacman.pos

            target = (
                pacman.pos[0] + random.randint(-3, 3),
                pacman.pos[1] + random.randint(-3, 3)
            )

            target = (
                max(0, min(COLS - 1, target[0])),
                max(0, min(ROWS - 1, target[1]))
            )

            if is_wall(*target):

                return pacman.pos

            return target

        return pacman.pos

    def update(self, pacman):

        if self.dead:

            return

        self.repath_timer -= 1

        if self.repath_timer <= 0:

            target = self.choose_target(pacman)

            self.path = astar(
                self.pos,
                target
            )

            self.repath_timer = 12

        if len(self.path) > 1:

            self.pos = self.path[1]

            self.path = self.path[1:]

    def draw(self):

        x, y = grid_to_pixel(self.pos)

        color = FRIGHTENED if self.frightened else self.color

        pygame.draw.circle(
            screen,
            color,
            (x, y - 3),
            TILE // 2 - 2
        )

        rect = pygame.Rect(
            x - TILE // 2 + 2,
            y,
            TILE - 4,
            TILE // 2
        )

        pygame.draw.rect(
            screen,
            color,
            rect
        )

        # Eyes

        pygame.draw.circle(
            screen,
            WHITE,
            (x - 6, y - 5),
            5
        )

        pygame.draw.circle(
            screen,
            WHITE,
            (x + 6, y - 5),
            5
        )

        pygame.draw.circle(
            screen,
            BLACK,
            (x - 5, y - 5),
            2
        )

        pygame.draw.circle(
            screen,
            BLACK,
            (x + 5, y - 5),
            2
        )


# =========================
# GAME
# =========================

class Game:

    def __init__(self):

        self.pacman = Pacman()

        self.ghosts = [

            Ghost(
                (9, 10),
                RED,
                "Blinky",
                "CHASE"
            ),

            Ghost(
                (10, 10),
                PINK,
                "Pinky",
                "AMBUSH"
            ),

            Ghost(
                (11, 10),
                CYAN,
                "Inky",
                "RANDOM"
            ),

            Ghost(
                (10, 11),
                ORANGE,
                "Clyde",
                "SMART"
            )
        ]

        self.score = 0

        self.lives = 3

        self.level = 1

        self.game_state = "START"

        self.power_timer = 0

        self.pellets = set()

        self.power_pellets = set()

        self.tick_counter = 0

        self.create_pellets()

    def create_pellets(self):

        self.pellets.clear()

        self.power_pellets.clear()

        for y in range(ROWS):

            for x in range(COLS):

                cell = MAZE[y][x]

                if cell == ".":

                    self.pellets.add((x, y))

                elif cell == "o":

                    self.power_pellets.add((x, y))

    def reset_positions(self):

        self.pacman.reset()

        for ghost in self.ghosts:

            ghost.reset()

        self.power_timer = 0

    def start_game(self):

        self.score = 0

        self.lives = 3

        self.level = 1

        self.create_pellets()

        self.reset_positions()

        self.game_state = "PLAYING"

    def next_level(self):

        self.level += 1

        self.create_pellets()

        self.reset_positions()

    def collect_items(self):

        pos = self.pacman.pos

        if pos in self.pellets:

            self.pellets.remove(pos)

            self.score += 10

        if pos in self.power_pellets:

            self.power_pellets.remove(pos)

            self.score += 50

            self.power_timer = 600

            for ghost in self.ghosts:

                ghost.frightened = True

    def check_collisions(self, old_pacman_pos, old_ghost_positions):

        for ghost in self.ghosts:

            if ghost.dead:
                continue

            if ghost.pos == self.pacman.pos or (ghost.pos == old_pacman_pos and old_ghost_positions[ghost.name] == self.pacman.pos):

                if ghost.frightened:

                    ghost.dead = True

                    self.score += 200

                else:

                    self.lives -= 1

                    if self.lives <= 0:

                        self.game_state = "GAMEOVER"

                    else:

                        self.reset_positions()

                    return

    def update(self):

        if self.game_state != "PLAYING":

            return

        self.pacman.anim += 0.25
        self.tick_counter += 1

        if self.tick_counter >= 8:
            self.tick_counter = 0

            old_pacman_pos = self.pacman.pos
            old_ghost_positions = {ghost.name: ghost.pos for ghost in self.ghosts}

            self.pacman.update()

            for ghost in self.ghosts:
                ghost.update(self.pacman)

            self.collect_items()
            self.check_collisions(old_pacman_pos, old_ghost_positions)

            if not self.pellets and not self.power_pellets:
                self.next_level()

        if self.power_timer > 0:

            self.power_timer -= 1

        else:

            for ghost in self.ghosts:

                ghost.frightened = False

    def draw_maze(self):

        for y in range(ROWS):

            for x in range(COLS):

                cell = MAZE[y][x]

                px = x * TILE

                py = y * TILE

                if cell == "#":

                    pygame.draw.rect(
                        screen,
                        BLUE,
                        (
                            px,
                            py,
                            TILE,
                            TILE
                        )
                    )

                    pygame.draw.rect(
                        screen,
                        LIGHT_BLUE,
                        (
                            px + 3,
                            py + 3,
                            TILE - 6,
                            TILE - 6
                        ),
                        2
                    )

        for x, y in self.pellets:

            px, py = grid_to_pixel((x, y))

            pygame.draw.circle(
                screen,
                WHITE,
                (px, py),
                3
            )

        for x, y in self.power_pellets:

            px, py = grid_to_pixel((x, y))

            pygame.draw.circle(
                screen,
                WHITE,
                (px, py),
                8
            )

    def draw_hud(self):

        pygame.draw.rect(
            screen,
            BLACK,
            (
                0,
                ROWS * TILE,
                WIDTH,
                70
            )
        )

        score_text = FONT.render(
            f"SCORE: {self.score}",
            True,
            WHITE
        )

        level_text = FONT.render(
            f"LEVEL: {self.level}",
            True,
            WHITE
        )

        lives_text = FONT.render(
            f"LIVES: {self.lives}",
            True,
            YELLOW
        )

        screen.blit(
            score_text,
            (15, ROWS * TILE + 10)
        )

        screen.blit(
            level_text,
            (WIDTH // 2 - 50, ROWS * TILE + 10)
        )

        screen.blit(
            lives_text,
            (WIDTH - 120, ROWS * TILE + 10)
        )

        if self.power_timer > 0:

            power_text = SMALL_FONT.render(
                "POWER MODE",
                True,
                CYAN
            )

            screen.blit(
                power_text,
                (
                    WIDTH // 2 - 55,
                    ROWS * TILE + 42
                )
            )

    def draw_start_screen(self):

        screen.fill(BLACK)

        title = BIG_FONT.render(
            "AI PAC-MAN",
            True,
            YELLOW
        )

        subtitle = FONT.render(
            "Powered by A* Pathfinding",
            True,
            CYAN
        )

        instruction = FONT.render(
            "Press ENTER to Start",
            True,
            WHITE
        )

        controls = SMALL_FONT.render(
            "Arrow Keys / WASD to move",
            True,
            WHITE
        )

        screen.blit(
            title,
            (
                WIDTH // 2 - title.get_width() // 2,
                HEIGHT // 2 - 120
            )
        )

        screen.blit(
            subtitle,
            (
                WIDTH // 2 - subtitle.get_width() // 2,
                HEIGHT // 2 - 55
            )
        )

        screen.blit(
            instruction,
            (
                WIDTH // 2 - instruction.get_width() // 2,
                HEIGHT // 2 + 20
            )
        )

        screen.blit(
            controls,
            (
                WIDTH // 2 - controls.get_width() // 2,
                HEIGHT // 2 + 65
            )
        )

    def draw_game_over(self):

        screen.fill(BLACK)

        title = BIG_FONT.render(
            "GAME OVER",
            True,
            RED
        )

        score = FONT.render(
            f"Final Score: {self.score}",
            True,
            WHITE
        )

        retry = FONT.render(
            "Press ENTER to Play Again",
            True,
            YELLOW
        )

        screen.blit(
            title,
            (
                WIDTH // 2 - title.get_width() // 2,
                HEIGHT // 2 - 100
            )
        )

        screen.blit(
            score,
            (
                WIDTH // 2 - score.get_width() // 2,
                HEIGHT // 2
            )
        )

        screen.blit(
            retry,
            (
                WIDTH // 2 - retry.get_width() // 2,
                HEIGHT // 2 + 60
            )
        )

    def draw(self):

        if self.game_state == "START":

            self.draw_start_screen()

            return

        if self.game_state == "GAMEOVER":

            self.draw_game_over()

            return

        screen.fill(BLACK)

        self.draw_maze()

        self.pacman.draw()

        for ghost in self.ghosts:

            ghost.draw()

        self.draw_hud()


# =========================
# MAIN LOOP
# =========================

game = Game()

running = True

while running:

    clock.tick(FPS)

    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            running = False

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:

                running = False

            if event.key == pygame.K_RETURN:

                if game.game_state in [
                    "START",
                    "GAMEOVER"
                ]:

                    game.start_game()

            if event.key in KEY_DIRS:

                game.pacman.next_direction = KEY_DIRS[event.key]

    game.update()

    game.draw()

    pygame.display.flip()

pygame.quit()

sys.exit()