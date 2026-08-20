import pygame  # type: ignore
from mazegenerator import MazeGenerator  # type: ignore


class PacSpriteSheet():

    CELL = 47
    SPRITE_W = 42
    SPRITE_H = 42

    def __init__(self, filename: str) -> None:
        self.sheet = pygame.image.load(filename).convert_alpha()

    def get_sprite(self, x: int, y: int, w: int, h: int) -> pygame.Surface:
        sprite = pygame.Surface((w, h), pygame.SRCALPHA)
        sprite.blit(self.sheet, (0, 0), (x, y, w, h))
        return sprite

    def get_sprite_at(
            self, row: int, col: int, w: int | None = None,
            h: int | None = None) -> pygame.Surface:
        w = w or self.SPRITE_W
        h = h or self.SPRITE_H
        return self.get_sprite(col * self.CELL, row * self.CELL, w, h)


class Pacwoman:
    def __init__(self, x: int, y: int, sprite_sheet: PacSpriteSheet,
                 screen_w: int, screen_y: int) -> None:
        self.x = x
        self.y = y
        self.screen_w = screen_w
        self.screen_y = screen_y
        self.direction = (1, 0)
        self.next_direction = (1, 0)
        self.move_speed = 3
        self.animation_speed = 3.5
        self.move_timer = 0
        self.frame_index = 0
        self.state = "idle"
        self.frame_sets = {
            (-1, 0): [sprite_sheet.get_sprite_at(8, 17),
                      sprite_sheet.get_sprite_at(7, 17),
                      sprite_sheet.get_sprite_at(6, 17)],
            (1, 0): [sprite_sheet.get_sprite_at(0, 17),
                     sprite_sheet.get_sprite_at(1, 17),
                     sprite_sheet.get_sprite_at(2, 17)],
            (0, 1): [sprite_sheet.get_sprite_at(3, 17),
                     sprite_sheet.get_sprite_at(4, 17),
                     sprite_sheet.get_sprite_at(5, 17)],
            (0, -1): [sprite_sheet.get_sprite_at(9, 17),
                      sprite_sheet.get_sprite_at(10, 17),
                      sprite_sheet.get_sprite_at(11, 17)]
        }
        self.current_frame = self.frame_sets[self.direction][0]
        self.death_frame_sets = [
            sprite_sheet.get_sprite_at(0, 7),
            sprite_sheet.get_sprite_at(1, 7),
            sprite_sheet.get_sprite_at(2, 7),
            sprite_sheet.get_sprite_at(3, 7),
            sprite_sheet.get_sprite_at(4, 7),
            sprite_sheet.get_sprite_at(5, 7),
            sprite_sheet.get_sprite_at(6, 7),
            sprite_sheet.get_sprite_at(7, 7),
            sprite_sheet.get_sprite_at(8, 7),
            sprite_sheet.get_sprite_at(9, 7),
            sprite_sheet.get_sprite_at(10, 7),
        ]
        self.death_animation_speed = 8
        self.death_frame_index = 0
        self.death_timer = 0

    def start_death_animation(self) -> None:
        self.state = "dying"
        self.death_frame_index = 0
        self.death_timer = 0
        self.death_hold_timer = 0
        self.death_hold_duration = 30

    def is_death_animation_done(self) -> bool:
        return (self.death_frame_index >= len(self.death_frame_sets) - 1
                and self.death_hold_timer >= self.death_hold_duration)

    def input(self, keys: pygame.key.ScancodeWrapper) -> None:
        requested = None
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            requested = (-1, 0)
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            requested = (1, 0)
        elif keys[pygame.K_UP] or keys[pygame.K_w]:
            requested = (0, -1)
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            requested = (0, 1)

        if requested is not None:
            self.next_direction = requested
            self.state = "moving"

    def move(self, mazegen: MazeGenerator) -> None:
        if self.state != "moving":
            return

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
        wall_bit = {(0, -1): 1,
                    (1, 0): 2,
                    (0, 1): 4,
                    (-1, 0): 8}

        if self.next_direction != self.direction:
            if not (cell & wall_bit[self.next_direction]):
                self.direction = self.next_direction

        dx, dy = self.direction

        offset = (MAZE_CELL - PacSpriteSheet.SPRITE_W) // 2
        if dx != 0:
            self.y = row * MAZE_CELL + offset
        elif dy != 0:
            self.x = col * MAZE_CELL + offset

        new_x = self.x + dx * self.move_speed
        new_y = self.y + dy * self.move_speed

        if cell & wall_bit[self.direction]:
            if dx == 1:
                new_x = min(new_x, col * MAZE_CELL +
                            (MAZE_CELL - PacSpriteSheet.SPRITE_W))
            elif dx == -1:
                new_x = max(new_x, col * MAZE_CELL)
            elif dy == 1:
                new_y = min(new_y, row * MAZE_CELL +
                            (MAZE_CELL - PacSpriteSheet.SPRITE_H))
            elif dy == -1:
                new_y = max(new_y, row * MAZE_CELL)

        clamped_x = max(0, min(self.screen_w - PacSpriteSheet.SPRITE_W, new_x))
        clamped_y = max(0, min(self.screen_y - PacSpriteSheet.SPRITE_H, new_y))

        if clamped_x == self.x and clamped_y == self.y:
            self.state = "idle"
        else:
            self.x, self.y = clamped_x, clamped_y

    def update(self) -> None:
        if self.state == "dying":
            self.current_frame = self.death_frame_sets[self.death_frame_index]

            if self.death_frame_index >= len(self.death_frame_sets) - 1:
                self.death_hold_timer += 1
                return

            self.death_timer += 1
            if self.death_timer >= self.death_animation_speed:
                self.death_timer = 0
                self.death_frame_index += 1
            return

        if self.state == "moving":
            self.move_timer += 1
            if self.move_timer >= self.animation_speed:
                self.move_timer = 0
                self.frame_index = (self.frame_index + 1) % len(
                    self.frame_sets[self.direction])
            self.current_frame = self.frame_sets[
                                                 self.direction][
                                                 self.frame_index]
        elif self.state == "idle":
            self.current_frame = self.frame_sets[self.direction][0]

    def draw(self, surface: pygame.surface.Surface) -> None:
        surface.blit(self.current_frame, (self.x, self.y))
