import pygame
import random
# from pygame.locals import *


TILEWIDTH = 16
TILEHEIGHT = 16
NROWS = 60
NCOLS = 100
SCREENWIDTH = NCOLS * TILEWIDTH
SCREENHEIGHT = NROWS * TILEHEIGHT
SCREENSIZE = (SCREENWIDTH, SCREENHEIGHT)
BLACK = (0, 0, 0)

class GameController(object):
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(SCREENSIZE, 0, 32)
        self.background = None
        # self.clock = pygame.time.Clock()

    def set_background(self):
        self.background = pygame.surface.Surface(SCREENSIZE).convert()
        self.background.fill(BLACK)

    def start_game(self):
        self.set_background()

    def update(self):
        """function called once per frame of the game == our game loop
        """
        self.check_events()

    def check_events(self):
        """check different events, for now checking if the player clicks
        exit
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

    def render(self):
        """draw images to the screen"""
        pygame.display.flip()


class Sprite(pygame.sprite.Sprite):
    def __init__(self, image):
        super().__init__()

        self.image = image

        self.rect = self.image.get_rect()


if __name__ == "__main__":
    game = GameController()
    game.set_background()

    # container class to hold and manage mutliple sprite objects
    all_sprites_list = pygame.sprite.Group()
    pacman = Sprite(pygame.image.load('sprites/pacman.png'))
    all_sprites_list.add(pacman)

    while True:
        game.update()
        all_sprites_list.draw(game.screen)
        game.render()
