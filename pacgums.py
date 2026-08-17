import pygame
from pacwoman import PacSpriteSheet

MAZE_CELL = 50


class Pacgums:
    def __init__(self, sprite_sheet: PacSpriteSheet, gum_row: int,
                 gum_col: int, sp_gum_row: int, sp_gum_col: int,
                 scared_duration: float = 10.0):
        self.gums: set = set()
        self.score: int = 0
        self.eat_ghosts: bool = False
        self.scared_duration: float = scared_duration
        self.scared_timer: float = 0.0

        self.pacgum_img = pygame.transform.scale(
            sprite_sheet.get_sprite_at(gum_row, gum_col), (25, 25))
        self.sp_pacgum_img = pygame.transform.scale(
            sprite_sheet.get_sprite_at(sp_gum_row, sp_gum_col), (30, 30))

    def init_gums(self, mazegen, pacwoman):
        # en double ?
        self.gums = set()
        self.super_gum = set()
        self.eat_ghosts = False
        self.scared_timer = 0.0

        pac_col = (pacwoman.x + PacSpriteSheet.SPRITE_W // 2) // MAZE_CELL
        pac_row = (pacwoman.y + PacSpriteSheet.SPRITE_H // 2) // MAZE_CELL

        for row, lines in enumerate(mazegen.maze):
            for col, cell in enumerate(lines):
                if cell != 15:
                    self.gums.add((row, col))

        self.gums.discard((pac_row, pac_col))

        maze_height = len(mazegen.maze)
        maze_width = len(mazegen.maze[0])
        corners = [
            (0, 0),
            (0, maze_width - 1),
            (maze_height - 1, 0),
            (maze_height - 1, maze_width - 1)
        ]

        for row, col in corners:
            self.gums.discard((row, col))
            self.super_gum.add((row, col))

        self.score = 0

    def eat(self, pacwoman):
        center_x = pacwoman.x + PacSpriteSheet.SPRITE_W // 2
        center_y = pacwoman.y + PacSpriteSheet.SPRITE_H // 2
        col = center_x // MAZE_CELL
        row = center_y // MAZE_CELL

        if (row, col) in self.gums:
            self.gums.discard((row, col))
            self.score += 10
        elif (row, col) in self.super_gum:
            self.super_gum.discard((row, col))
            self.score += 50
            self.eat_ghosts = True
            self.scared_timer = self.scared_duration

    def update(self, dt: float):
        if self.eat_ghosts:
            self.scared_timer -= dt
        if self.scared_timer <= 0:
            self.eat_ghosts = False
            self.scared_timer = 0.0

    def draw(self, screen):
        for row, col in self.gums:
            cx = col * MAZE_CELL
            cy = row * MAZE_CELL
            screen.blit(self.pacgum_img, (cx + 15.5, cy + 16.5))

        for row, col in self.super_gum:
            cx = col * MAZE_CELL
            cy = row * MAZE_CELL
            screen.blit(self.sp_pacgum_img, (cx + 15.5, cy + 16.5))
