import pygame
# import random
import pygame_menu
from pygame_menu import themes
import mazegenerator  # type: ignore
from parsing import parse
from movements import PacSpriteSheet, Pacwoman
from ghosts import Ghosts


TILEWIDTH = 16
TILEHEIGHT = 16
NROWS = 60
NCOLS = 100
SCREENWIDTH = NCOLS * TILEWIDTH
SCREENHEIGHT = NROWS * TILEHEIGHT
SCREENSIZE = (SCREENWIDTH, SCREENHEIGHT)
BLACK = (0, 0, 0)
PINK = (255, 209, 220)
BLINKY = (255,   0,   0)
INKY = (161, 255, 254)
PINKY = (255, 192, 203)
CLYDE = (255, 165,   0)

# create surface for the game to be a square and change values
# like for draw maze to percentage of the screen


class GameController(object):
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(SCREENSIZE, 0, 32)
        self.background = None
        self.running = True

    def set_background(self) -> None:
        self.background = pygame.Surface(SCREENSIZE).convert()
        self.background.fill(BLACK)

    def update(self) -> None:
        """function called once per frame of the game == our game loop
        call the function that checks the user inputs, and makes the ghosts
        move
        """
        self.check_events()
        keys = pygame.key.get_pressed()
        pacman.input(keys)
        pacman.move(mazegen)
        pacman.update()
        # blinky.input(keys)
        blinky.move_random(mazegen)
        blinky.update()
        all_sprites_list.update()
        # move ghosts

    def check_events(self) -> None:
        """check user inputs, which keys are pressed"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                # find a way to resume game after, instead of starting again
                if event.key == pygame.K_ESCAPE:
                    self.running = False

    def render(self, mazegen) -> None:
        """draw images to the screen"""
        # draw background
        self.set_background()
        # draw interface (score, lives, etc)

        # draw maze
        self.draw_maze(mazegen)
        # draw gums
        self.add_gums(mazegen)
        # draw sprites
        # all_sprites_list.draw(self.screen)
        pacman.draw(self.screen)
        blinky.draw(self.screen)
        # updates the screen with everything just drawn
        pygame.display.flip()

    def add_gums(self, mazegen) -> None:
        gum = pygame.transform.scale(
            pygame.image.load('sprites/pretzel.png').convert(), (16, 15))
        cx: float = 0
        cy: float = 0

        for line in mazegen.maze:
            for cell in line:
                if cell != 15:
                    self.screen.blit(gum, (cx + 15.5, cy + 16.5))
                cx += 50
            cx = 0
            cy += 50

    def draw_maze(self, mazegen) -> None:
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

    def start_game(self) -> None:
        """create maze, check user inputs and render new elements"""
        self.clock = pygame.time.Clock()
        self.time = 0.0
        # print(self.clock)
        while self.running:
            # menu.main_menu._open(loading)
            self.screen.fill("black")
            self.update()
            self.time += self.clock.tick(60) / 1000
            self.time = round(self.time, 2)
            # print(self.time)
            self.render(mazegen)
            # game ends after 90 seconds and goes back to menu
            if self.time == 90.00:
                self.running = False
        self.running = True

    def set_difficulty(self, difficulty) -> None:
        """select difficulty level from menu"""
        pass

    # def select_level(main_menu):
    #     main_menu._open(level)
    # call check events ? to check which choice the user makes
    # for ex we have 10 buttons, so in check events, if button #10
    # is pressed, then call function for level 10


if __name__ == "__main__":
    configuration = parse()
    game = GameController()
    game.set_background()
    mazegen = mazegenerator.MazeGenerator()

    # container class to hold and manage mutliple sprite objects
    all_sprites_list: pygame.sprite.Group = pygame.sprite.Group()

    sprite_sheet = PacSpriteSheet("sprites/pac_sheet.png")
    entry_x, entry_y = mazegen.maze_entry
    spawn_x = entry_x * 50 + (50 - PacSpriteSheet.SPRITE_H) // 2
    spawn_y = entry_y * 50 + (50 - PacSpriteSheet.SPRITE_W) // 2
    pacman = Pacwoman(spawn_x, spawn_y, sprite_sheet, SCREENWIDTH, SCREENHEIGHT)

    # Ghosts
    spawn_x_blky = len(mazegen.maze[0]) - 1
    spawn_y_blky = len(mazegen.maze) - 1
    blinky = Ghosts(
        spawn_x_blky, spawn_y_blky, sprite_sheet, SCREENWIDTH, SCREENHEIGHT)

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
