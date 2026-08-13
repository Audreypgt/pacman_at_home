import pygame
import random
from collections import deque


class PacSpriteSheet():
    CELL = 47
    SPRITE_W = 42
    SPRITE_H = 42

    def __init__(self, filename) -> None:
        self.sheet = pygame.image.load(filename).convert_alpha()

    def get_sprite(self, x, y, w, h) -> pygame.Surface:
        sprite = pygame.Surface((w, h), pygame.SRCALPHA)
        sprite.blit(self.sheet, (0, 0), (x, y, w, h))
        return sprite

    def get_sprite_at(self, row, col, w=None, h=None) -> pygame.Surface:
        w = w or self.SPRITE_W
        h = h or self.SPRITE_H
        return self.get_sprite(col * self.CELL, row * self.CELL, w, h)


class Pacwoman:
    def __init__(self, x, y, sprite_sheet, screen_w, screen_y) -> None:
        self.x = x
        self.y = y
        self.screen_w = screen_w
        self.screen_y = screen_y
        self.direction = (1, 0)
        self.move_speed = 3
        self.animation_speed = 3.5
        self.move_timer = 0
        self.frame_index = 0
        self.state = "idle"
        self.frame_sets = {
            (-1, 0): [
                sprite_sheet.get_sprite_at(8, 17),
                sprite_sheet.get_sprite_at(7, 17),
                sprite_sheet.get_sprite_at(6, 17)],
            (1, 0): [
                sprite_sheet.get_sprite_at(0, 17),
                sprite_sheet.get_sprite_at(1, 17),
                sprite_sheet.get_sprite_at(2, 17)],
            (0, 1): [
                sprite_sheet.get_sprite_at(3, 17),
                sprite_sheet.get_sprite_at(4, 17),
                sprite_sheet.get_sprite_at(5, 17)],
            (0, -1): [
                sprite_sheet.get_sprite_at(9, 17),
                sprite_sheet.get_sprite_at(10, 17),
                sprite_sheet.get_sprite_at(11, 17)]
        }
        self.current_frame = self.frame_sets[self.direction][0]

    def input(self, keys) -> None:
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.direction = (-1, 0)
            self.state = "moving"
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.direction = (1, 0)
            self.state = "moving"
        elif keys[pygame.K_UP] or keys[pygame.K_w]:
            self.direction = (0, -1)
            self.state = "moving"
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.direction = (0, 1)
            self.state = "moving"

    def move(self, mazegen) -> None:
        if self.state != "moving":
            return

        MAZE_CELL = 50
        dx, dy = self.direction

        maze_height = len(mazegen.maze)
        maze_width = len(mazegen.maze[0])

        center_x = self.x + PacSpriteSheet.SPRITE_W // 2
        center_y = self.y + PacSpriteSheet.SPRITE_H // 2
        col = center_x // MAZE_CELL
        row = center_y // MAZE_CELL

        if not (0 <= row < maze_height and 0 <= col < maze_width):
            self.state = "idle"
            return

        cell = mazegen.maze[row][col]
        wall_bit = {
            (0, -1): 1,
            (1, 0): 2,
            (0, 1): 4,
            (-1, 0): 8
            }[self.direction]

        offset = (MAZE_CELL - PacSpriteSheet.SPRITE_W) // 2
        if dx != 0:
            self.y = row * MAZE_CELL + offset
        elif dy != 0:
            self.x = col * MAZE_CELL + offset

        new_x = self.x + dx * self.move_speed
        new_y = self.y + dy * self.move_speed

        if cell & wall_bit:
            if dx == 1:
                new_x = min(
                    new_x, col * MAZE_CELL + (
                        MAZE_CELL - PacSpriteSheet.SPRITE_W))
            elif dx == -1:
                new_x = max(new_x, col * MAZE_CELL)
            elif dy == 1:
                new_y = min(
                    new_y, row * MAZE_CELL + (
                        MAZE_CELL - PacSpriteSheet.SPRITE_H))
            elif dy == -1:
                new_y = max(new_y, row * MAZE_CELL)

        clamped_x = max(0, min(self.screen_w - PacSpriteSheet.SPRITE_W, new_x))
        clamped_y = max(0, min(self.screen_y - PacSpriteSheet.SPRITE_H, new_y))

        if clamped_x == self.x and clamped_y == self.y:
            self.state = "idle"
        else:
            self.x, self.y = clamped_x, clamped_y

    def update(self) -> None:
        if self.state == "moving":
            self.move_timer += 1
            if self.move_timer >= self.animation_speed:
                self.move_timer = 0
                self.frame_index = (self.frame_index + 1) % len(
                    self.frame_sets[self.direction])
            self.current_frame = self.frame_sets[self.direction][
                self.frame_index]

    def draw(self, surface) -> None:
        surface.blit(self.current_frame, (self.x, self.y))


class Ghosts(Pacwoman):
    def __init__(self, x, y, sprite_sheet, screen_w, screen_y):
        super().__init__(x, y, sprite_sheet, screen_w, screen_y)
        self.direction = (1, 0)
        self.state = "moving"
        self.frame_sets = {}

    def choose_random_direction(self, mazegen) -> None:
        MAZE_CELL = 50

        directions = {
            (0, -1): 1,
            (1, 0): 2,
            (0, 1): 4,
            (-1, 0): 8}

        maze_height = len(mazegen.maze)
        maze_width = len(mazegen.maze[0])

        center_x = self.x + PacSpriteSheet.SPRITE_W // 2
        center_y = self.y + PacSpriteSheet.SPRITE_H // 2
        col = center_x // MAZE_CELL
        row = center_y // MAZE_CELL

        if not (0 <= row < maze_height and 0 <= col < maze_width):
            self.state = "idle"
            return

        cell = mazegen.maze[row][col]
        wall_bit = {
            (0, -1): 1,
            (1, 0): 2,
            (0, 1): 4,
            (-1, 0): 8
            }[self.direction]

        possible_directions = []

        for direction, wall_bit in directions.items():
            if not (cell & wall_bit):
                possible_directions.append(direction)

        if possible_directions:
            self.direction = random.choice(possible_directions)
            self.state = "moving"

    def move_random(self, mazegen) -> None:
        if self.state != "moving":
            self.choose_random_direction(mazegen)

        super().move(mazegen)

        if self.state == "idle":
            self.choose_random_direction(mazegen)


class Blinky(Ghosts):
    def __init__(self, x, y, sprite_sheet, screen_w, screen_y) -> None:
        super().__init__(x, y, sprite_sheet, screen_w, screen_y)

        self.frame_sets = {
            # West
            (-1, 0): [
                sprite_sheet.get_sprite_at(4, 0),
                sprite_sheet.get_sprite_at(5, 0)
                ],
            # East
            (1, 0): [
                sprite_sheet.get_sprite_at(0, 0),
                sprite_sheet.get_sprite_at(1, 0),
                ],
            # South
            (0, 1): [
                sprite_sheet.get_sprite_at(2, 0),
                sprite_sheet.get_sprite_at(3, 0),
                ],
            # North
            (0, -1): [
                sprite_sheet.get_sprite_at(6, 0),
                sprite_sheet.get_sprite_at(7, 0)
                ]
        }

    def choose_bfs_direction(self, mazegen, pacwoman) -> None:
        self.neighbors: list[tuple[str, int, int]] = []

        for row in range(len(mazegen.maze)):
            for col in range(len(mazegen.maze[row])):
                cell = mazegen.maze[row][col]
                # North
                if not (cell & 1):
                    self.neighbors.append(("N", row, col))
                # East
                if not (cell & 2):
                    self.neighbors.append(("E", row, col))
                # South
                if not (cell & 4):
                    self.neighbors.append(("S", row, col))
                # West
                if not (cell & 8):
                    self.neighbors.append(("W", row, col))

        path: list[tuple[int, int]] = []
        pacwoman_loc = pacwoman.x, pacwoman.y
        queue: deque[tuple[int, int]] = deque()
        # curr_x, curr_y = self.x, self.y
        # queue.append((curr_y, curr_x))
        queue.append((self.x, self.y))
        parent: dict[tuple[int, int], tuple[int, int] | None] = {
            (self.x, self.y): None}
        visited: dict[tuple[int, int], str] = {}

        while queue:
            print(f"path is {path}")
            curr_cell: list[tuple[int, int]] = []
            curr_cell.append(queue.popleft())
            visited.update({curr_cell[-1]: "visited"})

            print(f"curr_cell is {curr_cell[-1]}")
            if curr_cell[-1] == pacwoman_loc:
                for cell in curr_cell:
                    path.append(cell)
                    cell = parent[cell]
                path = path[::-1]
                break

            for _, row, col in self.neighbors:
                if not visited.get((row, col)):
                    parent.update({(row, col): (curr_cell[-1])})
                    queue.append((row, col))

        next_x, next_y = path[-1]
        self.direction = (self.x + next_x), (self.y + next_y)

    def bfs_move(self, mazegen, pacwoman) -> None:
        if self.state != "moving":
            self.choose_bfs_direction(mazegen, pacwoman)

        super().move(mazegen)

        if self.state == "idle":
            self.choose_bfs_direction(mazegen, pacwoman)


class Pinky(Ghosts):
    def __init__(self, x, y, sprite_sheet, screen_w, screen_y) -> None:
        super().__init__(x, y, sprite_sheet, screen_w, screen_y)

        self.frame_sets = {
            # West
            (-1, 0): [
                sprite_sheet.get_sprite_at(4, 1),
                sprite_sheet.get_sprite_at(5, 1)
                ],
            # East
            (1, 0): [
                sprite_sheet.get_sprite_at(0, 1),
                sprite_sheet.get_sprite_at(1, 1),
                ],
            # South
            (0, 1): [
                sprite_sheet.get_sprite_at(2, 1),
                sprite_sheet.get_sprite_at(3, 1),
                ],
            # North
            (0, -1): [
                sprite_sheet.get_sprite_at(6, 1),
                sprite_sheet.get_sprite_at(7, 1)
                ]
        }


class Clyde(Ghosts):
    def __init__(self, x, y, sprite_sheet, screen_w, screen_y) -> None:
        super().__init__(x, y, sprite_sheet, screen_w, screen_y)

        self.frame_sets = {
            # West
            (-1, 0): [
                sprite_sheet.get_sprite_at(4, 3),
                sprite_sheet.get_sprite_at(5, 3)
                ],
            # East
            (1, 0): [
                sprite_sheet.get_sprite_at(0, 3),
                sprite_sheet.get_sprite_at(1, 3),
                ],
            # South
            (0, 1): [
                sprite_sheet.get_sprite_at(2, 3),
                sprite_sheet.get_sprite_at(3, 3),
                ],
            # North
            (0, -1): [
                sprite_sheet.get_sprite_at(6, 3),
                sprite_sheet.get_sprite_at(7, 3)
                ]
        }


class Inky(Ghosts):
    def __init__(self, x, y, sprite_sheet, screen_w, screen_y) -> None:
        super().__init__(x, y, sprite_sheet, screen_w, screen_y)

        self.frame_sets = {
            # West
            (-1, 0): [
                sprite_sheet.get_sprite_at(4, 2),
                sprite_sheet.get_sprite_at(5, 2)
                ],
            # East
            (1, 0): [
                sprite_sheet.get_sprite_at(0, 2),
                sprite_sheet.get_sprite_at(1, 2),
                ],
            # South
            (0, 1): [
                sprite_sheet.get_sprite_at(2, 2),
                sprite_sheet.get_sprite_at(3, 2),
                ],
            # North
            (0, -1): [
                sprite_sheet.get_sprite_at(6, 2),
                sprite_sheet.get_sprite_at(7, 2)
                ]
        }
