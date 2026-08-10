import pygame


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

        offset = (MAZE_CELL - PacSpriteSheet.SPRITE_W) // 2
        if dx != 0:
            self.y = row * MAZE_CELL + offset
        elif dy != 0:
            self.x = col * MAZE_CELL + offset


        maze_pixel_w = maze_width * MAZE_CELL
        maze_pixel_h = maze_height * MAZE_CELL
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
