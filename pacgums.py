import pygame
from pacwoman import PacSpriteSheet

# def add_gums(mazegen, screen) -> None:
#         gum = pygame.transform.scale(
#             pygame.image.load('sprites/pretzel.png').convert(), (16, 15))
#         cx: float = 0
#         cy: float = 0

#         for line in mazegen.maze:
#             for cell in line:
#                 if cell != 15:
#                     screen.blit(gum, (cx + 15.5, cy + 16.5))
#                 cx += 50
#             cx = 0
#             cy += 50

MAZE_CELL = 50

class Pacgums:
    def __init__(self, image_path: srt = "sprites/pretzel.png"):
        self.gums = set()
        self.score = 0
        self.image = pygame.transform.scale(pygame.image.load(image_path).convert_alpha(), (16, 15))

    def init_gums(self, mazegen):
        self.gums = set()
        for row, lines in enumerate(mazegen.maze):
            for col, cell in enumerate(lines):
                if cell != 15:
                    self.gums.add((row, col))
        self.score = 0

    def eat(self, pacman):
        center_x = pacman.x + PacSpriteSheet.SPRITE_W // 2
        center_y = pacman.y + PacSpriteSheet.SPRITE_H // 2
        col = center_x // MAZE_CELL
        row = center_y // MAZE_CELL
        if (row, col) in self.gums:
            self.gums.discard((row, col))
            self.score += 10
            print(self.score)

    def draw(self, screen):
        for row, col in self.gums:
            cx = col * MAZE_CELL
            cy = row * MAZE_CELL
            screen.blit(self.image, (cx + 15.5, cy + 16.5))