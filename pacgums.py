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
    def __init__(self, image_path: 'sprite/pretzel.png'):
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

    def eat(self):
        pass

    def draw(self, screen):
        for row, col in self.gums:
            cx = col * MAZE_CELL
            cy = row * MAZE_CELL
            screen.blit(image(cx + 15.5, cy + 16.5))