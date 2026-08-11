import pygame
# import random
import pygame_menu
from pygame_menu import themes
import mazegenerator  # type: ignore
from parsing import parse
from pacwoman import PacSpriteSheet, Pacwoman
from ghosts import Blinky, Pinky, Clyde, Inky
from pacgums import Pacgums


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
        self.running = False
        self.over = False
        self.pacgums = Pacgums()

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
        self.pacwoman.input(keys)
        self.pacwoman.move(self.mazegen)
        self.pacwoman.update()
        self.pacgums.eat(self.pacwoman)
        # all_sprites_list.update(pacman)
        # move ghosts
        self.blinky.move_random(self.mazegen)
        self.blinky.update()
        self.pinky.move_random(self.mazegen)
        self.pinky.update()
        self.clyde.move_random(self.mazegen)
        self.clyde.update()
        self.inky.move_random(self.mazegen)
        self.inky.update()

    def check_events(self) -> None:
        """check user inputs, which keys are pressed"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                # find a way to resume game after, instead of starting again
                if event.key == pygame.K_ESCAPE:
                    self.pause_menu()
                    self.paused = True
                    # self.running = False

    def render(self, mazegen) -> None:
        """draw images to the screen"""
        # draw background
        self.set_background()
        # draw interface (score, lives, etc)
        # draw maze
        self.draw_maze(mazegen)
        # draw gums
        self.pacgums.draw(self.screen)
        # draw sprites
        self.pacwoman.draw(self.screen)
        self.blinky.draw(self.screen)
        self.pinky.draw(self.screen)
        self.clyde.draw(self.screen)
        self.inky.draw(self.screen)
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

    def set_up_game(self) -> None:
        if self.over:
            with open(configuration.highscore_filename, 'a') as f:
                f.write(
                    f"{self.looser.get_value()}: {self.pacgums.score}\n")
            self.sort_score_file()
            self.over = False
        self.clock = pygame.time.Clock()
        self.time = 0.0
        self.running = True
        pac_sheet = PacSpriteSheet("sprites/pac_sheet.png")

        # Pacwoman
        entry_x, entry_y = self.mazegen.maze_entry
        spawn_x = entry_x * 50 + (50 - PacSpriteSheet.SPRITE_W) // 2
        spawn_y = entry_y * 50 + (50 - PacSpriteSheet.SPRITE_H) // 2
        self.pacwoman = Pacwoman(
            spawn_x, spawn_y, pac_sheet, SCREENWIDTH, SCREENHEIGHT)

        # Pacgums
        self.pacgums.init_gums(game.mazegen)

        # Blinky
        spawn_x_blky = (
            len(game.mazegen.maze[0]) - 1) * 50 + (
                50 - PacSpriteSheet.SPRITE_W) // 2
        spawn_y_blky = (
            len(game.mazegen.maze) - 1) * 50 + (
                50 - PacSpriteSheet.SPRITE_H) // 2
        self.blinky = Blinky(
            spawn_x_blky, spawn_y_blky, pac_sheet, SCREENWIDTH, SCREENHEIGHT)

        # Pinky
        spawn_x_pky = (50 - PacSpriteSheet.SPRITE_W) // 2
        spawn_y_pky = (
            len(game.mazegen.maze) - 1) * 50 + (
                50 - PacSpriteSheet.SPRITE_H) // 2
        self.pinky = Pinky(
            spawn_x_pky, spawn_y_pky, pac_sheet, SCREENWIDTH, SCREENHEIGHT)

        # Clyde
        spawn_x_clyde = 0
        spawn_y_clyde = 0
        self.clyde = Clyde(
            spawn_x_clyde, spawn_y_clyde, pac_sheet, SCREENWIDTH, SCREENHEIGHT)

        # Inky
        spawn_x_inky = (len(game.mazegen.maze[0]) - 1) * 50 + (
                50 - PacSpriteSheet.SPRITE_W) // 2
        spawn_y_inky = (50 - PacSpriteSheet.SPRITE_H) // 2
        self.inky = Inky(
            spawn_x_inky, spawn_y_inky, pac_sheet, SCREENWIDTH, SCREENHEIGHT)

        self.start_game()

    def start_game(self) -> None:
        """create maze, check user inputs and render new elements"""
        # if not self.paused:
        # print(self.clock)
        self.paused = False
        while self.running:
            self.screen.fill("black")
            self.update()
            self.time += self.clock.tick(60) / 1000
            self.time = round(self.time, 2)
            # print(self.time)
            self.render(self.mazegen)
            # game ends after 90 seconds and goes back to menu
            if self.time >= 2:
                self.running = False
                self.over_menu()

    def sort_score_file(self):
        with open(configuration.highscore_filename, 'r') as f:
            txt = f.read()
        scores_list = txt.split("\n")
        scores_dict = {}

        for line in scores_list:
            temp = line.split(": ")
            if len(temp) < 2:
                break
            scores_dict.update({temp[0]: temp[1]})

        scores_dict = dict(
            sorted(scores_dict.items(),
                   key=lambda item: item[1], reverse=True))
        with open(configuration.highscore_filename, 'w') as f:
            for name, score in scores_dict.items():
                f.write(
                    f"{name}: {score}\n")

    def quit_game_over(self):
        with open(configuration.highscore_filename, 'a') as f:
            f.write(
                f"{self.looser.get_value()}: {self.pacgums.score}\n")
        self.sort_score_file()
        pygame.quit()

    def start_menu(self):
        main_menu = pygame_menu.Menu(
            "PacWOman", 600, 400, theme=themes.THEME_SOLARIZED)
        main_menu.add.button("Play", self.set_up_game)
        # main_menu.add.button("Select level", select_level(main_menu))
        main_menu.add.button("Select level")
        # main_menu.add.button("Select difficulty??", game.set_difficulty)
        # select difficulty could send you to a menu page with only the
        # difficulty and a button like <hard> and when you press -> key it
        # changes the difficulty, then you press enter and you go back to
        # the main menu
        main_menu.add.button("Quit", pygame_menu.events.EXIT)
        main_menu.mainloop(self.screen)

    def pause_menu(self):
        main_menu = pygame_menu.Menu(
            "PacWOman", 600, 400, theme=themes.THEME_SOLARIZED)
        main_menu.add.button("Restart", self.set_up_game)
        main_menu.add.button("Resume", self.start_game)
        main_menu.add.button("Quit", pygame_menu.events.EXIT)
        main_menu.mainloop(self.screen)

    def over_menu(self):
        self.over = True
        main_menu = pygame_menu.Menu(
            "PacWOman", 600, 400, theme=themes.THEME_SOLARIZED)
        self.looser = main_menu.add.text_input("Name: ", default="LOOSER")
        main_menu.add.button("Restart", self.set_up_game)
        main_menu.add.button(
            "Give up like you did with your dreams", self.quit_game_over)
        # ERROR ================= pygame.error: video system not initialized
        main_menu.mainloop(game.screen)

    # def set_difficulty(self, difficulty) -> None:
    #     """select difficulty level from menu"""
    #     pass

    # def select_level(main_menu):
    #     main_menu._open(level)
    # call check events ? to check which choice the user makes
    # for ex we have 10 buttons, so in check events, if button #10
    # is pressed, then call function for level 10


if __name__ == "__main__":
    configuration = parse()
    game = GameController()
    game.set_background()
    game.mazegen = mazegenerator.MazeGenerator()

    # start from starting menu
    game.start_menu()
