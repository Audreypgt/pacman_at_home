import pygame
# import random
import pygame_menu
from pygame_menu import themes
import mazegenerator  # type: ignore
from parsing import parse


TILEWIDTH = 16
TILEHEIGHT = 16
NROWS = 60
NCOLS = 100
SCREENWIDTH = NCOLS * TILEWIDTH
SCREENHEIGHT = NROWS * TILEHEIGHT
SCREENSIZE = (SCREENWIDTH, SCREENHEIGHT)
BLACK = (0, 0, 0)
PINK = (255, 209, 220)

# create surface for the game to be a square and change values
# like for draw maze to percentage of the screen


class GameController(object):
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(SCREENSIZE, 0, 32)
        self.background = None
        self.running = True

    def set_background(self):
        self.background = pygame.Surface(SCREENSIZE).convert()
        self.background.fill(BLACK)

    def update(self):
        """function called once per frame of the game == our game loop
        call the function that checks the user inputs, and makes the ghosts
        move
        """
        self.check_events()
        all_sprites_list.update()
        # move ghosts

    def check_events(self):
        """check user inputs, which keys are pressed"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                # find a way to resume game after, instead of starting again
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    pacman.direction = (0, -1)
                if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    pacman.direction = (0, 1)
                if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    pacman.direction = (-1, 0)
                if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    pacman.direction = (1, 0)

    def render(self, mazegen):
        """draw images to the screen"""
        # draw background
        self.set_background()
        # draw interface (score, lives, etc)

        # draw maze
        self.draw_maze(mazegen)
        # draw sprites
        all_sprites_list.draw(self.screen)
        # updates the screen with everything just drawn
        pygame.display.flip()

    def draw_maze(self, mazegen):
        cy = 0
        cx = 0
        for line in mazegen.maze:
            for cell in line:
                # North
                if cell & 1:
                    pygame.draw.line(
                        game.screen, PINK, (cx, cy), (cx + 50, cy))
                # East
                if cell & 2:
                    pygame.draw.line(
                        game.screen, PINK, (cx + 50, cy), (cx + 50, cy + 50))
                # South
                if cell & 4:
                    pygame.draw.line(
                        game.screen, PINK, (cx, cy + 50), (cx + 50, cy + 50))
                # West
                if cell & 8:
                    pygame.draw.line(
                        game.screen, PINK, (cx, cy), (cx, cy + 50))
                cx += 50
            cy += 50
            cx = 0

        # 1 = 0001 Nord
        # 2 = 0010 Est
        # 4 = 0100 Sud
        # 8 = 1000 Ouest
        # 3 = 0011 Fermee au Nord et a l'Est
        # 15 = 1111 tout ferme

    def start_game(self):
        """create maze, check user inputs and render new elements"""
        mazegen = mazegenerator.MazeGenerator()
        self.clock = pygame.time.Clock()
        self.time = 0
        print(self.clock)
        while self.running:
            # menu.main_menu._open(loading)
            self.screen.fill("black")
            self.update()
            self.time += self.clock.tick(60) / 1000
            self.time = round(self.time, 2)
            print(self.time)
            self.render(mazegen)
            # game ends after 90 seconds and goes back to menu
            if self.time == 90.00:
                self.running = False
        self.running = True

    def set_difficulty(self, difficulty):
        """select difficulty level from menu"""
        pass

    # def select_level(main_menu):
    #     main_menu._open(level)
    # call check events ? to check which choice the user makes
    # for ex we have 10 buttons, so in check events, if button #10
    # is pressed, then call function for level 10


class Sprite(pygame.sprite.Sprite):
    def __init__(self, image):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.direction = (0, 0)
        self.speed = 4

    def update(self):
        self.rect.x += self.direction[0] * self.speed
        self.rect.y += self.direction[1] * self.speed




if __name__ == "__main__":
    configuration = parse()
    game = GameController()
    game.set_background()

    # container class to hold and manage mutliple sprite objects
    all_sprites_list: pygame.sprite.Group = pygame.sprite.Group()
    pacman = Sprite(pygame.image.load('sprites/pacman.png'))
    all_sprites_list.add(pacman)

    # Menu
    main_menu = pygame_menu.Menu(
        "Pacman", 600, 400, theme=themes.THEME_SOLARIZED)
    main_menu.add.text_input("Name: ", default="username")
    main_menu.add.button("Play", game.start_game)
    main_menu.add.button("Resume")
    # main_menu.add.button("Select level", select_level(main_menu))
    main_menu.add.button("Select level")
    # main_menu.add.button("Select difficulty??", game.set_difficulty)
    # select difficulty could send you to a menu page with only the
    # difficulty and a button like <hard> and when you press -> key it
    # changes the difficulty, then you press enter and you go back to
    # the main menu
    main_menu.add.button("Quit", pygame_menu.events.EXIT)
    main_menu.mainloop(game.screen)
