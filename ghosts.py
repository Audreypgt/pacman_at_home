import pygame
import random
from collections import deque
from pacwoman import PacSpriteSheet, Pacwoman
from mazegenerator import MazeGenerator


class Ghosts(Pacwoman):
    def __init__(self, x: int, y: int, sprite_sheet: PacSpriteSheet,
                 screen_w: int, screen_y: int) -> None:
        super().__init__(x, y, sprite_sheet, screen_w, screen_y)
        self.direction: tuple[int, int] = (1, 0)
        self.state: str = "moving"
        self.frame_sets: dict[
            tuple[int, int], list[pygame.Surface]] = {}
        # maybe replace self.scared with self.ghost_state from pac-man ?
        self.scared: bool = False
        self.warning: bool = False
        self.on_spawn = False
        self.dead: bool = False
        self.ghost_state = "normal"
        self.scared_frame_sets: dict[
            tuple[int, int], list[pygame.Surface]] = {
            (-1, 0): [
                sprite_sheet.get_sprite_at(15, 0),
                sprite_sheet.get_sprite_at(16, 0)],
            (1, 0): [
                sprite_sheet.get_sprite_at(11, 0),
                sprite_sheet.get_sprite_at(12, 0)],
            (0, 1): [
                sprite_sheet.get_sprite_at(13, 0),
                sprite_sheet.get_sprite_at(14, 0)],
            (0, -1): [
                sprite_sheet.get_sprite_at(17, 0),
                sprite_sheet.get_sprite_at(18, 0)]
        }
        self.flash_frame_sets: dict[
            tuple[int, int], list[pygame.Surface]] = {
            (-1, 0): [
                sprite_sheet.get_sprite_at(15, 0),
                sprite_sheet.get_sprite_at(16, 1)],
            (1, 0): [
                sprite_sheet.get_sprite_at(11, 0),
                sprite_sheet.get_sprite_at(12, 1)],
            (0, 1): [
                sprite_sheet.get_sprite_at(13, 0),
                sprite_sheet.get_sprite_at(14, 1)],
            (0, -1): [
                sprite_sheet.get_sprite_at(17, 0),
                sprite_sheet.get_sprite_at(18, 1)]
        }
        self.dead_frame_sets: dict[
            tuple[int, int], list[pygame.Surface]] = {
            (-1, 0): [sprite_sheet.get_sprite_at(7, 6)],
            (1, 0): [sprite_sheet.get_sprite_at(5, 6)],
            (0, 1): [sprite_sheet.get_sprite_at(6, 6)],
            (0, -1): [sprite_sheet.get_sprite_at(8, 6)]
        }

        self.move_speed = 1
        self.animation_speed = 1.5
        self.flash_animation_speed = 8
        self.coord_x = (self.x + self.sprite_w // 2) // 50
        self.coord_y = (self.y + self.sprite_h // 2) // 50
        self.curr_cell: tuple[int, int] = (self.coord_x, self.coord_y)

    def update(self) -> None:
        if self.dead:
            active_frames = self.dead_frame_sets
            self.frame_index = (self.frame_index + 1) % len(
                active_frames[self.direction])
            self.move_speed = 2
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
        offset = (MAZE_CELL - self.sprite_w) // 2
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

        center_x = self.x + self.sprite_w // 2
        center_y = self.y + self.sprite_h // 2
        col = center_x // MAZE_CELL
        row = center_y // MAZE_CELL

        if not (0 <= row < maze_height and 0 <= col < maze_width):
            self.state = "idle"
            return

        cell = mazegen.maze[row][col]
        reverse = (-self.direction[0], -self.direction[1])
        possible_directions = []
        for direction, wall_bit in {
            (0, -1): 1,
            (1, 0): 2,
            (0, 1): 4,
            (-1, 0): 8
        }.items():
            if not (cell & wall_bit):
                possible_directions.append(direction)

        # classic rule: no immediate U-turn unless it is the only way out
        non_reverse = [d for d in possible_directions if d != reverse]
        if non_reverse:
            possible_directions = non_reverse

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
        """Return True when the ghost reached its spawn cell, else follow
        the BFS path toward it (used for respawn and scatter states)."""
        self.coord_x, self.coord_y = self.current_cell()
        spawn_cell = ((spawn_x + self.sprite_w // 2) // 50,
                      (spawn_y + self.sprite_w // 2) // 50)

        if (self.coord_x, self.coord_y) == spawn_cell:
            self.dead = False
            self.scared = False
            self.warning = False
            self.ghost_state = "normal"
            self.move_speed = 1
            return True

        self.bfs_direction(mazegen, spawn_cell)
        return False

    def bfs_direction(self, mazegen: MazeGenerator,
                      target: tuple[int, int]) -> None:
        """BFS the shortest path to the target cell (x, y), then set the
        direction to its first step. Falls back to a random direction if
        no path is found."""
        self.coord_x, self.coord_y = self.current_cell()
        queue: deque[tuple[int, int]] = deque()
        visited: set[tuple[int, int]] = set()
        visited.add((self.coord_x, self.coord_y))
        queue.append((self.coord_x, self.coord_y))
        parent: dict[tuple[int, int], tuple[int, int] | None] = {
            (self.coord_x, self.coord_y): None}

        # BFS algorithm to find shortest path to target
        while queue:
            v_x, v_y = queue.popleft()
            if (v_x, v_y) == target:
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

        path: list[tuple[int, int]] = [target]
        while True:
            next_step = parent[path[-1]]
            if not next_step:
                break
            path.append(next_step)

        path = path[::-1]

        if len(path) >= 2:
            next_x, next_y = path[1]
            next_dir = (next_x - self.coord_x), (next_y - self.coord_y)
            # classic rule: no immediate U-turn unless it is the only way
            reverse = (-self.direction[0], -self.direction[1])
            if next_dir == reverse:
                alternatives = [
                    d for d in self.find_neighbors(
                        mazegen, self.coord_x, self.coord_y)
                    if d != reverse]
                if alternatives:
                    distances = self.bfs_distances(mazegen, target)
                    next_dir = min(
                        alternatives,
                        key=lambda d: distances.get(
                            (self.coord_x + d[0], self.coord_y + d[1]),
                            float("inf")))
            self.direction = next_dir
            self.next_direction = next_dir
            self.state = "moving"
        else:
            self.choose_random_direction(mazegen)

    def distance_to(self, other: Pacwoman) -> int:
        """manhattan distance in maze cells to another sprite"""
        own_x, own_y = self.current_cell()
        other_x, other_y = other.current_cell()
        return abs(own_x - other_x) + abs(own_y - other_y)

    def snap_to_cell_center(self) -> None:
        """realign the sprite on its cell's centre slot"""
        col = (self.x + self.sprite_w // 2) // 50
        row = (self.y + self.sprite_h // 2) // 50
        offset = (50 - self.sprite_w) // 2
        self.x = col * 50 + offset
        self.y = row * 50 + offset

    def crossed_cell_center(self, old_x: int, old_y: int) -> bool:
        offset = (50 - self.sprite_w) // 2
        for old, new in ((old_x, self.x), (old_y, self.y)):
            if old == new:
                continue
            delta = (old - offset) % 50
            if delta == 0:
                continue
            if new < old:
                if new <= old - delta:
                    return True
            else:
                if new >= old + (50 - delta):
                    return True
        return False

    def scatter_move(self, mazegen: MazeGenerator, spawn_x: int, spawn_y: int
                     ) -> None:
        self.on_spawn = False

        if self.state != "moving":
            self.snap_to_cell_center()
            self.on_spawn = self.scatter_mode(mazegen, spawn_x, spawn_y)

        if not self.on_spawn:
            old_x, old_y = self.x, self.y
            super().move(mazegen)

            if (self.crossed_cell_center(
                    old_x, old_y) and self.state == "moving"):
                self.snap_to_cell_center()
                self.on_spawn = self.scatter_mode(mazegen, spawn_x, spawn_y)

        self.curr_cell = ((self.x + self.sprite_w // 2) // 50,
                          (self.y + self.sprite_h // 2) // 50)

    def bfs_distances(
            self, mazegen: MazeGenerator,
            target: tuple[int, int]) -> dict[tuple[int, int], int]:
        """BFS from target: BFS distance of every reachable cell"""
        maze_width = len(mazegen.maze[0])
        maze_height = len(mazegen.maze)
        if not (0 <= target[0] < maze_width and 0 <= target[1] < maze_height):
            return {}
        distances: dict[tuple[int, int], int] = {target: 0}
        queue: deque[tuple[int, int]] = deque([target])
        while queue:
            v_x, v_y = queue.popleft()
            for dir_x, dir_y in self.find_neighbors(mazegen, v_x, v_y):
                new_cell = (v_x + dir_x, v_y + dir_y)
                if new_cell not in distances:
                    distances[new_cell] = distances[(v_x, v_y)] + 1
                    queue.append(new_cell)
        return distances

    def choose_bfs_direction(
            self, mazegen: MazeGenerator, pacwoman: Pacwoman,
            pinky: bool) -> None:
        """follow the BFS path to pacwoman; when pinky is True the target
        is 4 cells ahead of her, to ambush instead of chase"""
        pw_x, pw_y = pacwoman.current_cell()

        if pinky:
            pw_dir_x, pw_dir_y = pacwoman.direction
            pw_x += pw_dir_x * 4
            pw_y += pw_dir_y * 4

        pw_x = max(0, min(pw_x, len(mazegen.maze[0]) - 1))
        pw_y = max(0, min(pw_y, len(mazegen.maze) - 1))

        self.bfs_direction(mazegen, (pw_x, pw_y))


class Blinky(Ghosts):
    def __init__(self, x: int, y: int, sprite_sheet: PacSpriteSheet,
                 screen_w: int, screen_y: int) -> None:
        super().__init__(x, y, sprite_sheet, screen_w, screen_y)

        self.frame_sets = {
            # West
            (-1, 0): [
                sprite_sheet.get_sprite_at(4, 0),
                sprite_sheet.get_sprite_at(5, 0)],
            # East
            (1, 0): [
                sprite_sheet.get_sprite_at(0, 0),
                sprite_sheet.get_sprite_at(1, 0),],
            # South
            (0, 1): [
                sprite_sheet.get_sprite_at(2, 0),
                sprite_sheet.get_sprite_at(3, 0),],
            # North
            (0, -1): [
                sprite_sheet.get_sprite_at(6, 0),
                sprite_sheet.get_sprite_at(7, 0)]
        }

    def bfs_move(self, mazegen: MazeGenerator, pacwoman: Pacwoman) -> None:
        if self.state != "moving":
            self.choose_bfs_direction(mazegen, pacwoman, False)
        super().move(mazegen)

        if self.is_centered() and self.state == "moving":
            self.choose_bfs_direction(mazegen, pacwoman, False)

        curr_x = (self.x + self.sprite_w // 2) // 50
        curr_y = (self.y + self.sprite_h // 2) // 50
        self.curr_cell = (curr_x, curr_y)


class Pinky(Ghosts):
    def __init__(self, x: int, y: int, sprite_sheet: PacSpriteSheet,
                 screen_w: int, screen_y: int) -> None:
        super().__init__(x, y, sprite_sheet, screen_w, screen_y)
        self.frame_sets = {
            # West
            (-1, 0): [
                sprite_sheet.get_sprite_at(4, 1),
                sprite_sheet.get_sprite_at(5, 1)],
            # East
            (1, 0): [
                sprite_sheet.get_sprite_at(0, 1),
                sprite_sheet.get_sprite_at(1, 1),],
            # South
            (0, 1): [
                sprite_sheet.get_sprite_at(2, 1),
                sprite_sheet.get_sprite_at(3, 1),],
            # North
            (0, -1): [
                sprite_sheet.get_sprite_at(6, 1),
                sprite_sheet.get_sprite_at(7, 1)]
        }

    def bfs_move(self, mazegen: MazeGenerator, pacwoman: Pacwoman) -> None:
        if self.state != "moving":
            self.choose_bfs_direction(mazegen, pacwoman, True)
        super().move(mazegen)

        if self.is_centered() and self.state == "moving":
            self.choose_bfs_direction(mazegen, pacwoman, True)

        curr_x = (self.x + self.sprite_w // 2) // 50
        curr_y = (self.y + self.sprite_h // 2) // 50
        self.curr_cell = (curr_x, curr_y)


class Clyde(Ghosts):
    """chases pacwoman, but runs back to his corner when she gets too
    close"""

    SHY_RADIUS = 8

    def __init__(self, x: int, y: int, sprite_sheet: PacSpriteSheet,
                 screen_w: int, screen_y: int) -> None:
        super().__init__(x, y, sprite_sheet, screen_w, screen_y)

        self.frame_sets = {
            # West
            (-1, 0): [
                sprite_sheet.get_sprite_at(4, 3),
                sprite_sheet.get_sprite_at(5, 3)],
            # East
            (1, 0): [
                sprite_sheet.get_sprite_at(0, 3),
                sprite_sheet.get_sprite_at(1, 3),],
            # South
            (0, 1): [
                sprite_sheet.get_sprite_at(2, 3),
                sprite_sheet.get_sprite_at(3, 3),],
            # North
            (0, -1): [
                sprite_sheet.get_sprite_at(6, 3),
                sprite_sheet.get_sprite_at(7, 3)]
        }

    def chase_or_retreat(self, mazegen: MazeGenerator, pacwoman: Pacwoman,
                         spawn_x: int, spawn_y: int) -> None:
        """chase pacwoman, or walk home when she is closer than
        SHY_RADIUS cells"""
        corner = ((spawn_x + self.sprite_w // 2) // 50,
                  (spawn_y + self.sprite_w // 2) // 50)
        if self.distance_to(pacwoman) < Clyde.SHY_RADIUS:
            self.bfs_direction(mazegen, corner)
        else:
            self.choose_bfs_direction(mazegen, pacwoman, False)

    def clyde_move(self, mazegen: MazeGenerator, pacwoman: Pacwoman,
                   spawn_x: int, spawn_y: int) -> None:
        if self.state != "moving":
            self.chase_or_retreat(mazegen, pacwoman, spawn_x, spawn_y)
        super().move(mazegen)

        if self.is_centered() and self.state == "moving":
            self.chase_or_retreat(mazegen, pacwoman, spawn_x, spawn_y)


class Inky(Ghosts):
    """hunts pacwoman from far away, but wanders randomly
    once close to her"""

    WANDER_RADIUS = 8

    def __init__(self, x: int, y: int, sprite_sheet: PacSpriteSheet,
                 screen_w: int, screen_y: int) -> None:
        super().__init__(x, y, sprite_sheet, screen_w, screen_y)

        self.frame_sets = {
            # West
            (-1, 0): [
                sprite_sheet.get_sprite_at(4, 2),
                sprite_sheet.get_sprite_at(5, 2)],
            # East
            (1, 0): [
                sprite_sheet.get_sprite_at(0, 2),
                sprite_sheet.get_sprite_at(1, 2),],
            # South
            (0, 1): [
                sprite_sheet.get_sprite_at(2, 2),
                sprite_sheet.get_sprite_at(3, 2),],
            # North
            (0, -1): [
                sprite_sheet.get_sprite_at(6, 2),
                sprite_sheet.get_sprite_at(7, 2)]
        }

    def hunt_or_wander(self, mazegen: MazeGenerator, pacwoman: Pacwoman
                       ) -> None:
        """chase pacwoman, or move randomly when closer than
        WANDER_RADIUS cells"""
        if self.distance_to(pacwoman) > Inky.WANDER_RADIUS:
            self.choose_bfs_direction(mazegen, pacwoman, False)
        else:
            self.choose_random_direction(mazegen)

    def inky_move(self, mazegen: MazeGenerator, pacwoman: Pacwoman) -> None:
        if self.state != "moving":
            self.hunt_or_wander(mazegen, pacwoman)
        super().move(mazegen)

        if self.is_centered() and self.state == "moving":
            self.hunt_or_wander(mazegen, pacwoman)
