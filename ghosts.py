import pygame  # type: ignore
import random
from collections import deque
from pacwoman import PacSpriteSheet, Pacwoman
from mazegenerator import MazeGenerator  # type: ignore


class Ghosts(Pacwoman):
    def __init__(self, x: int, y: int, sprite_sheet: pygame.surface.Surface,
                 screen_w: int, screen_y: int) -> None:
        super().__init__(x, y, sprite_sheet, screen_w, screen_y)
        self.direction: tuple[int, int] = (1, 0)
        self.state: str = "moving"
        self.frame_sets: dict[tuple[int, int], pygame.Surface] = {}
        # maybe replace self.scared with self.ghost_state from pac-man ?
        self.scared: bool = False
        self.warning: bool = False
        self.on_spawn = False
        self.dead: bool = False
        self.ghost_state = "normal"
        self.scared_frame_sets: dict[tuple[int, int], pygame.Surface] = {
            (-1, 0): [
                sprite_sheet.get_sprite_at(15, 0),
                sprite_sheet.get_sprite_at(16, 0)
                ],
            (1, 0): [
                sprite_sheet.get_sprite_at(11, 0),
                sprite_sheet.get_sprite_at(12, 0)
                ],
            (0, 1): [
                sprite_sheet.get_sprite_at(13, 0),
                sprite_sheet.get_sprite_at(14, 0)
                ],
            (0, -1): [
                sprite_sheet.get_sprite_at(17, 0),
                sprite_sheet.get_sprite_at(18, 0)
                ]
        }
        self.flash_frame_sets: dict[tuple[int, int], pygame.Surface] = {
            (-1, 0): [
                sprite_sheet.get_sprite_at(15, 0),
                sprite_sheet.get_sprite_at(16, 1)
                ],
            (1, 0): [
                sprite_sheet.get_sprite_at(11, 0),
                sprite_sheet.get_sprite_at(12, 1)
                ],
            (0, 1): [
                sprite_sheet.get_sprite_at(13, 0),
                sprite_sheet.get_sprite_at(14, 1)
                ],
            (0, -1): [
                sprite_sheet.get_sprite_at(17, 0),
                sprite_sheet.get_sprite_at(18, 1)
                ]
        }
        self.dead_frame_sets: dict[tuple[int, int], pygame.Surface] = {
            (-1, 0): [sprite_sheet.get_sprite_at(7, 6)],
            (1, 0): [sprite_sheet.get_sprite_at(5, 6)],
            (0, 1): [sprite_sheet.get_sprite_at(6, 6)],
            (0, -1): [sprite_sheet.get_sprite_at(8, 6)]
        }

        self.move_speed = 1
        self.animation_speed = 1.5
        self.flash_animation_speed = 8
        self.coord_x = (self.x + PacSpriteSheet.SPRITE_W // 2) // 50
        self.coord_y = (self.y + PacSpriteSheet.SPRITE_H // 2) // 50
        self.curr_cell: tuple[int, int] = (self.coord_x, self.coord_y)

    def update(self) -> None:
        if self.dead:
            active_frames = self.dead_frame_sets
            self.frame_index = (self.frame_index + 1) % len(
                    active_frames[self.direction])
            self.move_speed = 3
        elif self.scared and self.warning:
            flash_on = (pygame.time.get_ticks() // 200) % 2 == 0
            active_frames = (
                self.flash_frame_sets if flash_on else self.scared_frame_sets)
        elif self.scared:
            active_frames = self.scared_frame_sets
        else:
            active_frames = self.frame_sets

        if self.state == "moving":
            self.move_timer += 1
            if self.move_timer >= self.flash_animation_speed:
                self.move_timer = 0
                self.frame_index = (self.frame_index + 1) % len(
                    active_frames[self.direction])
        self.current_frame = active_frames[self.direction][self.frame_index]

    def is_centered(self) -> bool:
        MAZE_CELL = 50
        offset = (MAZE_CELL - PacSpriteSheet.SPRITE_W) // 2
        return (self.x - offset) % MAZE_CELL == 0 and \
            (self.y - offset) % MAZE_CELL == 0

    def find_neighbors(self, mazegen: MazeGenerator, x: int, y: int
                       ) -> list[tuple[int, int]]:
        neighbors: list[tuple[int, int]] = []

        if not (mazegen.maze[y][x] & 1):
            neighbors.append((0, -1))
        if not (mazegen.maze[y][x] & 2):
            neighbors.append((1, 0))
        if not (mazegen.maze[y][x] & 4):
            neighbors.append((0, 1))
        if not (mazegen.maze[y][x] & 8):
            neighbors.append((-1, 0))

        return neighbors

    def choose_random_direction(self, mazegen: MazeGenerator) -> None:
        MAZE_CELL = 50

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
        # reverse = (-self.direction[0], -self.direction[1])
        possible_directions = []
        for direction, wall_bit in {
            (0, -1): 1,
            (1, 0): 2,
            (0, 1): 4,
            (-1, 0): 8
        }.items():
            if not (cell & wall_bit):
                possible_directions.append(direction)

        # non_reverse = [d for d in possible_directions if d != reverse]
        # if non_reverse:
        #     possible_directions = non_reverse

        if possible_directions:
            self.direction = random.choice(possible_directions)
            self.next_direction = self.direction
            self.state = "moving"

    def move_random(self, mazegen: MazeGenerator) -> None:
        if self.state != "moving":
            self.choose_random_direction(mazegen)

        super().move(mazegen)

        if self.is_centered() and self.state == "moving":
            self.choose_random_direction(mazegen)

        if self.state == "idle":
            self.choose_random_direction(mazegen)

    def scatter_mode(self, mazegen: MazeGenerator, spawn_x: int, spawn_y: int
                     ) -> bool:
        self.coord_x = (self.x + PacSpriteSheet.SPRITE_W // 2) // 50
        self.coord_y = (self.y + PacSpriteSheet.SPRITE_H // 2) // 50
        spawn_x = (spawn_x + PacSpriteSheet.SPRITE_W // 2) // 50
        spawn_y = (spawn_y + PacSpriteSheet.SPRITE_W // 2) // 50

        if (self.coord_x, self.coord_y) == (spawn_x, spawn_y):
            self.dead = False
            self.scared = False
            self.warning = False
            self.ghost_state = "normal"
            self.move_speed = 1
            return True

        spawn_loc = spawn_x, spawn_y
        queue: deque[tuple[int, int]] = deque()
        visited: set[tuple[int, int]] = set()
        visited.add((self.coord_x, self.coord_y))
        queue.append((self.coord_x, self.coord_y))
        parent: dict[tuple[int, int], tuple[int, int] | None] = {
            (self.coord_x, self.coord_y): None}
        parent.update({(self.coord_x, self.coord_y): None})

        # BFS algorithm to find shortest path to spawn_loc
        while queue:
            v_x, v_y = queue.popleft()
            if (v_x, v_y) == spawn_loc:
                break
            for edges in self.find_neighbors(mazegen, v_x, v_y):
                dir_x, dir_y = edges
                new_x, new_y = v_x + dir_x, v_y + dir_y
                if (0 <= new_x < len(mazegen.maze[0])) \
                    and (0 <= new_y < len(mazegen.maze)) \
                   and ((new_x), (new_y)) not in visited:
                    visited.add((new_x, new_y))
                    parent.update({((new_x), (new_y)): (v_x, v_y)})
                    queue.append(((new_x), (new_y)))

        path: list[tuple[int, int]] = [spawn_loc]
        while parent.get(path[-1]) is not None:
            path.append(parent[path[-1]])
        path = path[::-1]

        if len(path) >= 2:
            next_x, next_y = path[1]
            self.direction = (next_x - self.coord_x), (next_y - self.coord_y)
            self.next_direction = self.direction
            self.state = "moving"
            return False
        else:
            self.choose_random_direction(mazegen)
            return False

        return False

    def scatter_move(self, mazegen: MazeGenerator, spawn_x: int, spawn_y: int
                     ) -> None:
        self.on_spawn = False

        if self.is_centered() and self.state != "moving":
            self.on_spawn = self.scatter_mode(mazegen, spawn_x, spawn_y)

        if not self.on_spawn:
            super().move(mazegen)

        curr_x = (self.x + PacSpriteSheet.SPRITE_W // 2) // 50
        curr_y = (self.y + PacSpriteSheet.SPRITE_H // 2) // 50

        if (curr_x, curr_y) != self.curr_cell and self.state == "moving":
            self.on_spawn = self.scatter_mode(mazegen, spawn_x, spawn_y)

        self.curr_cell = (curr_x, curr_y)


class Blinky(Ghosts):
    def __init__(self, x: int, y: int, sprite_sheet: PacSpriteSheet,
                 screen_w: int, screen_y: int) -> None:
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

    def choose_bfs_direction(
            self, mazegen: MazeGenerator, pacwoman: Pacwoman) -> None:
        # coords are received as nb of pixels so we convert to
        # (x, y) coordinates
        self.coord_x = (self.x + PacSpriteSheet.SPRITE_W // 2) // 50
        self.coord_y = (self.y + PacSpriteSheet.SPRITE_H // 2) // 50
        pw_x = (pacwoman.x + PacSpriteSheet.SPRITE_W // 2) // 50
        pw_y = (pacwoman.y + PacSpriteSheet.SPRITE_H // 2) // 50

        pacwoman_loc = pw_x, pw_y
        queue: deque[tuple[int, int]] = deque()
        visited: set[tuple[int, int]] = set()
        visited.add((self.coord_x, self.coord_y))
        queue.append((self.coord_x, self.coord_y))
        parent: dict[tuple[int, int], tuple[int, int] | None] = {
            (self.coord_x, self.coord_y): None}
        parent.update({(self.coord_x, self.coord_y): None})

        # BFS algorithm to find shortest path to pacman
        while queue:
            v_x, v_y = queue.popleft()
            if (v_x, v_y) == pacwoman_loc:
                break
            for edges in self.find_neighbors(mazegen, v_x, v_y):
                dir_x, dir_y = edges
                new_x, new_y = v_x + dir_x, v_y + dir_y
                if (0 <= new_x < len(mazegen.maze[0])) \
                    and (0 <= new_y < len(mazegen.maze)) \
                   and ((new_x), (new_y)) not in visited:
                    visited.add((new_x, new_y))
                    parent.update({((new_x), (new_y)): (v_x, v_y)})
                    queue.append(((new_x), (new_y)))

        path: list[tuple[int, int]] = [pacwoman_loc]
        while parent.get(path[-1]) is not None:
            path.append(parent[path[-1]])
        path = path[::-1]

        # Condition in case anything goes wrong and no path is found
        # even though it shouldn't happen
        if len(path) >= 2:
            # next step for ghost is second to last coordinates, since last
            # one is the current location
            next_x, next_y = path[1]
            self.direction = (next_x - self.coord_x), (next_y - self.coord_y)
            self.next_direction = self.direction
            self.state = "moving"
            return
        else:
            self.choose_random_direction(mazegen)
            return

    def bfs_move(self, mazegen: MazeGenerator, pacwoman: Pacwoman) -> None:
        if self.state != "moving":
            self.choose_bfs_direction(mazegen, pacwoman)
        super().move(mazegen)

        if self.is_centered() and self.state == "moving":
            self.choose_bfs_direction(mazegen, pacwoman)

        curr_x = (self.x + PacSpriteSheet.SPRITE_W // 2) // 50
        curr_y = (self.y + PacSpriteSheet.SPRITE_H // 2) // 50
        self.curr_cell = (curr_x, curr_y)


class Pinky(Ghosts):
    def __init__(self, x: int, y: int, sprite_sheet: PacSpriteSheet,
                 screen_w: int, screen_y: int) -> None:
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
    def __init__(self, x: int, y: int, sprite_sheet: PacSpriteSheet,
                 screen_w: int, screen_y: int) -> None:
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
    def __init__(self, x: int, y: int, sprite_sheet: PacSpriteSheet,
                 screen_w: int, screen_y: int) -> None:
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
