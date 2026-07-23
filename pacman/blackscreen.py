import pygame
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

    def set_background(self):
        self.background = pygame.surface.Surface(SCREENSIZE).convert()
        self.background.fill(BLACK)

    def start_game(self):
        self.set_background()

    def update(self):
        """function called once per frame of the game == our game loop
        """
        self.check_events()
        # self.render()

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
        pygame.display.update()


if __name__ == "__main__":
    game = GameController()
    game.set_background()
    while True:
        game.update()
