import pygame
from pacwoman import PacSpriteSheet
from random import choice

MAZE_CELL = 50


class Pacgums:
    def __init__(self, gum_path: set = "sprites/pretzel.png",
                 sp_gum_path: set = "sprites/test_gum.png"):
        self.gums = set()
        self.score = 0
        self.eat_ghosts: bool = False
        self.pacgum_img = pygame.transform.scale(
            pygame.image.load(gum_path).convert_alpha(), (16, 15))
        self.sp_pacgum_img = pygame.transform.scale(
            pygame.image.load(sp_gum_path).convert_alpha(), (16, 15))

    def init_gums(self, mazegen, pacwoman):
        self.gums = set()
        self.super_gum = set()
        center_x = pacwoman.x + PacSpriteSheet.SPRITE_W // 2
        center_y = pacwoman.y + PacSpriteSheet.SPRITE_H // 2

        for row, lines in enumerate(mazegen.maze):
            for col, cell in enumerate(lines):
                if cell != 15:
                    self.gums.add((row, col))

        rand_row = choice([i for i in range(0, len(mazegen.maze) - 1)
                           if i not in [center_x]])
        rand_col = choice([i for i in range(0, len(mazegen.maze[0]) - 1)
                           if i not in [center_y]])
        if mazegen.maze[rand_row][rand_col] == 15:
            while mazegen.maze[rand_row][rand_col] == 15:
                rand_row = choice([i for i in range(0, len(mazegen.maze) - 1)
                                   if i not in [center_x]])
                rand_col = choice([i for i in range(0, len(
                            mazegen.maze[0]) - 1) if i not in [center_y]])
        self.gums.discard((rand_row, rand_col))
        self.super_gum.add((rand_row, rand_col))

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
            # maybe get time here and wait like 20 sec (here or in file
            # pac-man ?) before turning bool back to false
            # add this part to pac-man file to allow pacwoman to eat ghosts
            self.eat_ghosts = True

            # code possibility to eat the fxcking ghosts then
            # print(self.score)

    def draw(self, screen):
        for row, col in self.gums:
            cx = col * MAZE_CELL
            cy = row * MAZE_CELL
            screen.blit(self.pacgum_img, (cx + 15.5, cy + 16.5))
        for row, col in self.super_gum:
            cx = col * MAZE_CELL
            cy = row * MAZE_CELL
            screen.blit(self.sp_pacgum_img, (cx + 15.5, cy + 16.5))
