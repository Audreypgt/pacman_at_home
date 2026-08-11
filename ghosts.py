import pygame
from movements import PacSpriteSheet
import random


class PacSpriteSheet():

    CELL = 47
    SPRITE_W = 42
    SPRITE_H = 42

    def __init__(self, filename):
        self.sheet = pygame.image.load(filename).convert_alpha()

    def get_sprite(self, x, y, w, h):
        sprite = pygame.Surface((w, h), pygame.SRCALPHA)
        sprite.blit(self.sheet, (0, 0), (x, y, w, h))
        return sprite

    def get_sprite_at(self, row, col, w=None, h=None):
        w = w or self.SPRITE_W
        h = h or self.SPRITE_H
        return self.get_sprite(col * self.CELL, row * self.CELL, w, h)

class Pacwoman:
    def __init__(self, x, y, sprite_sheet, screen_w, screen_y):
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
            (-1, 0): [sprite_sheet.get_sprite_at(8, 17) ,sprite_sheet.get_sprite_at(7, 17), sprite_sheet.get_sprite_at(6, 17)],
            (1, 0): [sprite_sheet.get_sprite_at(0, 17) ,sprite_sheet.get_sprite_at(1, 17), sprite_sheet.get_sprite_at(2, 17)],
            (0, 1): [sprite_sheet.get_sprite_at(3, 17), sprite_sheet.get_sprite_at(4, 17), sprite_sheet.get_sprite_at(5, 17)],
            (0, -1): [sprite_sheet.get_sprite_at(9, 17), sprite_sheet.get_sprite_at(10,17), sprite_sheet.get_sprite_at(11, 17)]
        }
        self.current_frame = self.frame_sets[self.direction][0]

    def input(self, keys):
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

    def move(self, mazegen):
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
        wall_bit = {(0, -1): 1, (1, 0): 2, (0, 1): 4, (-1, 0): 8}[self.direction]

        offset = (MAZE_CELL - PacSpriteSheet.SPRITE_W) // 2
        if dx != 0:
            self.y = row * MAZE_CELL + offset
        elif dy != 0:
            self.x = col * MAZE_CELL + offset

        new_x = self.x + dx * self.move_speed
        new_y = self.y + dy * self.move_speed

        if cell & wall_bit:
            if dx == 1:
                new_x = min(new_x, col * MAZE_CELL + (MAZE_CELL - PacSpriteSheet.SPRITE_W))
            elif dx == -1:
                new_x = max(new_x, col * MAZE_CELL)
            elif dy == 1:
                new_y = min(new_y, row * MAZE_CELL + (MAZE_CELL - PacSpriteSheet.SPRITE_H))
            elif dy == -1:
                new_y = max(new_y, row * MAZE_CELL)

        clamped_x = max(0, min(self.screen_w - PacSpriteSheet.SPRITE_W, new_x))
        clamped_y = max(0, min(self.screen_y - PacSpriteSheet.SPRITE_H, new_y))

        if clamped_x == self.x and clamped_y == self.y:
            self.state = "idle"
        else:
            self.x, self.y = clamped_x, clamped_y


    def update(self):
        if self.state == "moving":
            self.move_timer += 1
            if self.move_timer >= self.animation_speed:
                self.move_timer = 0
                self.frame_index = (self.frame_index + 1) % 3
            self.current_frame = self.frame_sets[self.direction][self.frame_index]

    def draw(self, surface):
        surface.blit(self.current_frame, (self.x, self.y))

class Ghosts(Pacwoman):
    def __init__(self, x, y, sprite_sheet, screen_w, screen_y):
        super().__init__(x, y, sprite_sheet, screen_w, screen_y)
        self.direction = (1, 0)
        self.state = "moving"
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


    def choose_random_direction(self, mazegen):
        MAZE_CELL = 50

        directions = {"N": (0, -1),
                 "E": (1, 0),
                 "S": (0, 1),
                 "W": (-1, 0)}

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
        wall_bit = {(0, -1): 1, (1, 0): 2, (0, 1): 4, (-1, 0): 8}[self.direction]

        possible_directions = []

        for direction, wall_bit in directions:
            if not (cell & wall_bit):
                possible_directions.append(direction)

        if possible_directions:
            self.direction = random.choice(possible_directions)
            self.state = "moving"

    def move_random(self, mazegen):
        if self.state != "moving":
            self.choose_random_direction(mazegen)

        super().move(mazegen)

        if self.state == "idle":
            self.choose_random_direction(mazegen)



    # def blinky_move(self, mazegen) -> None:
    #     MAZE_CELL = 50

    #     direc = {"N": (0, -1),
    #              "E": (1, 0),
    #              "S": (0, 1),
    #              "W": (-1, 0)}

    #     maze_height = len(mazegen.maze)
    #     maze_width = len(mazegen.maze[0])

    #     center_x = self.x + PacSpriteSheet.SPRITE_W // 2
    #     center_y = self.y + PacSpriteSheet.SPRITE_H // 2
    #     col = center_x // MAZE_CELL
    #     row = center_y // MAZE_CELL

    #     dx, dy = self.direction

    #     if not (0 <= row < maze_height and 0 <= col < maze_width):
    #         self.state = "idle"
    #         return

    #     cell = mazegen.maze[row][col]
    #     wall_bit = {(0, -1): 1, (1, 0): 2, (0, 1): 4, (-1, 0): 8}[
    #         self.direction]

    #     offset = (MAZE_CELL - PacSpriteSheet.SPRITE_W) // 2
    #     if dx != 0:
    #         self.y = row * MAZE_CELL + offset
    #     elif dy != 0:
    #         self.x = col * MAZE_CELL + offset

    #     new_x = self.x + dx * self.move_speed
    #     new_y = self.y + dy * self.move_speed

    #     if cell & wall_bit:
    #         if dx == 1:
    #             new_x = min(new_x, col * MAZE_CELL + (
    #                 MAZE_CELL - PacSpriteSheet.SPRITE_W))
    #         elif dx == -1:
    #             new_x = max(new_x, col * MAZE_CELL)
    #         elif dy == 1:
    #             new_y = min(new_y, row * MAZE_CELL + (
    #                 MAZE_CELL - PacSpriteSheet.SPRITE_H))
    #         elif dy == -1:
    #             new_y = max(new_y, row * MAZE_CELL)

    #     clamped_x = max(
    #         0, min(self.screen_w - PacSpriteSheet.SPRITE_W, new_x))
    #     clamped_y = max(
    #         0, min(self.screen_y - PacSpriteSheet.SPRITE_H, new_y))

    #     if clamped_x == self.x and clamped_y == self.y:
    #         self.blinky_move(mazegen)
    #     else:
    #         self.x, self.y = clamped_x, clamped_y

    # def update(self):
    #     self.move_timer += 1
    #     if self.move_timer >= self.animation_speed:
    #         self.move_timer = 0
    #         self.frame_index = (self.frame_index + 1) % 2
    #     self.current_frame = self.frame_sets[
    #       self.direction][self.frame_index]

    # def draw(self, surface):
    #     surface.blit(self.current_frame, (self.x, self.y))

    # Algo solver amazeing --------------------------------------------------
    # def algo(self) -> None:
    #     """Solve a perfect or imperfect maze using BFS algorithm and return
    #     a list of the cells that are part of the solution path
    #     """
    #     self.reset_path()
    #     for row in self.cells:
    #         for cel in row:
    #             cel.visited = False
    #             cel.neighbors = []

    #     dir_dict: dict[str, tuple[int, int]] = {
    #         'N': (0, -1),
    #         'S': (0, 1),
    #         'W': (-1, 0),
    #         'E': (1, 0)}
    #     directions = ['N', 'S', 'W', 'E']
    #     cell: list[list[Maze.Cell]] = self.cells

    #     # first, create a list of neighbors for each cell
    #     for y in range(self.height):
    #         for x in range(self.width):
    #             # check each open direction of the cell
    #             for direction in directions:
    #                 if not cell[y][x].walls[direction]:
    #                     # calculate possible neighbor's coordinates
    #                     dir_x, dir_y = dir_dict[direction]
    #                     nb_x, nb_y = x + dir_x, y + dir_y
    #                     # check if possible neighbor is inside the maze before
    #                     # adding it to the current cell's neighbors list
    #                     if 0 <= nb_x < self.width and 0 <= nb_y < self.height:
    #                         cell[y][x].neighbors.append(cell[nb_y][nb_x])

    #     # then find the path with BFS algorithm using a queue
    #     queue: deque[Maze.Cell] = deque()
    #     path: list[Maze.Cell] = []
    #     curr_x, curr_y = self.entry
    #     queue.append(cell[curr_y][curr_x])
    #     parent: dict[Maze.Cell, Maze.Cell | None] = {
    #         cell[curr_y][curr_x]: None}

    #     while queue:
    #         curr_cell = queue.popleft()
    #         curr_cell.visited = True

    #         if curr_cell.coord == self.exit:
    #             while curr_cell is not None:
    #                 path.append(curr_cell)
    #                 curr_cell.is_path = True
    #                 curr_cell = cast(Maze.Cell, parent[curr_cell])
    #             path = path[::-1]
    #             break
    #         for neighbor in curr_cell.neighbors:
    #             if not neighbor.visited:
    #                 parent[neighbor] = curr_cell
    #                 queue.append(neighbor)
    #     return path
