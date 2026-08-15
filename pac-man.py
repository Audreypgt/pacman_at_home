import pygame
# import random
import mazegenerator  # type: ignore
from parsing import parse
from pacwoman import PacSpriteSheet, Pacwoman
from ghosts import Blinky, Pinky, Clyde, Inky
from pacgums import Pacgums
from menu import Gamemenus


MAZE_CELL = 50
# change cols and rows with data from config file
MAZE_COLS = 15
MAZE_ROWS = 15
# change sizes to percentage to fit every screens
GUI_HEIGHT = 80

GAME_WIDTH = MAZE_COLS * MAZE_CELL + 1
GAME_HEIGHT = MAZE_ROWS * MAZE_CELL + 1
SCREENWIDTH = GAME_WIDTH
SCREENHEIGHT = GUI_HEIGHT + GAME_HEIGHT
SCREENSIZE = (SCREENWIDTH, SCREENHEIGHT)

BLACK = (0, 0, 0)
PINK = (255, 209, 220)


class GameController(object):
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(SCREENSIZE, 0, 32)
        self.game_surface = self.screen.subsurface(
            pygame.Rect(0, GUI_HEIGHT, GAME_WIDTH, GAME_HEIGHT))
        self.background = None
        self.running = False
        self.over = False
        self.pac_sheet = PacSpriteSheet("sprites/pac_sheet.png")
        self.pacgums = Pacgums(self.pac_sheet, gum_row=5, gum_col=8,
                               sp_gum_row=6, sp_gum_col=8)
        self.menus = Gamemenus(self)
        self.looser = ""

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
        self.pacwoman.move(mazegen)
        self.pacwoman.update()
        self.pacgums.eat(self.pacwoman)
        self.pacgums.update(self.clock.get_time() / 1000)
        
        for ghost in (self.blinky, self.inky, self.pinky, self.clyde):
            ghost.scared = self.pacgums.eat_ghosts
            ghost.warning = self.pacgums.eat_ghosts and self.pacgums.scared_timer <= 4

        self.blinky.bfs_move(mazegen, self.pacwoman)
        self.blinky.update()
        self.pinky.move_random(mazegen)
        self.pinky.update()
        self.clyde.move_random(mazegen)
        self.clyde.update()
        self.inky.move_random(mazegen)
        self.inky.update()

        self.check_collisions()

    def check_events(self) -> None:
        """check user inputs, which keys are pressed"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.menus.pause_menu()
                    self.paused = True

    def render(self, mazegen) -> None:
        """draw images to the screen"""
        # draw background
        self.screen.fill(BLACK, pygame.Rect(0, 0, SCREENWIDTH, GUI_HEIGHT))
        self.game_surface.fill(BLACK)
        # draw interface (score, lives, etc)

        # draw maze
        self.draw_maze(mazegen)
        # draw gums
        self.pacgums.draw(self.game_surface)
        # draw sprites
        self.pacwoman.draw(self.game_surface)
        self.blinky.draw(self.game_surface)
        self.pinky.draw(self.game_surface)
        self.clyde.draw(self.game_surface)
        self.inky.draw(self.game_surface)
        score_text = self.score_font.render(
            f'Score: {self.pacgums.score}', True, (255, 255, 255))
        self.screen.blit(score_text, (10, 10))
        timer_text = self.timer_font.render(
            f'Time: {int(self.time)}', True, (255, 255, 255))
        self.screen.blit(timer_text, (10, 50))
        pygame.display.flip()

    def draw_maze(self, mazegen) -> None:
        cy = 0
        cx = 0
        for line in mazegen.maze:
            for cell in line:
                # North
                if cell & 1:
                    pygame.draw.line(
                        self.game_surface, PINK, (cx, cy), (cx + 50, cy))
                # East
                if cell & 2:
                    pygame.draw.line(
                        self.game_surface, PINK, (cx + 50, cy), (cx + 50, cy + 50))
                # South
                if cell & 4:
                    pygame.draw.line(
                        self.game_surface, PINK, (cx, cy + 50), (cx + 50, cy + 50))
                # West
                if cell & 8:
                    pygame.draw.line(
                        self.game_surface, PINK, (cx, cy), (cx, cy + 50))
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
        self.time = 120.0
        self.running = True
        self.lives = 3
        self.invulnerable_timer = 0
        self.score_font = pygame.font.Font(None, 36)
        self.timer_font = pygame.font.Font(None, 36)
        pac_sheet = self.pac_sheet

        # Pacwoman
        maze_width = len(mazegen.maze[0])
        maze_height = len(mazegen.maze)
        center_col = maze_width // 2
        center_row = maze_height // 2
        spawn_x = center_col * 50 + (50 - PacSpriteSheet.SPRITE_W) // 2
        spawn_y = center_row * 50 + (50 - PacSpriteSheet.SPRITE_H) // 2
        self.pacwoman_spawn = (spawn_x, spawn_y)
        self.pacwoman = Pacwoman(
            spawn_x, spawn_y, pac_sheet, GAME_WIDTH, GAME_HEIGHT)

        # Pacgums
        self.pacgums.init_gums(mazegen, self.pacwoman)

        # Blinky
        spawn_x_blky = (
            len(mazegen.maze[0]) - 1) * 50 + (
                50 - PacSpriteSheet.SPRITE_W) // 2
        spawn_y_blky = (
            len(mazegen.maze) - 1) * 50 + (
                50 - PacSpriteSheet.SPRITE_H) // 2
        self.blinky_spawn = (spawn_x_blky, spawn_y_blky)
        self.blinky = Blinky(
            spawn_x_blky, spawn_y_blky, pac_sheet,
            GAME_WIDTH, GAME_HEIGHT)

        # Pinky
        spawn_x_pky = (50 - PacSpriteSheet.SPRITE_W) // 2
        spawn_y_pky = (
            len(mazegen.maze) - 1) * 50 + (
                50 - PacSpriteSheet.SPRITE_H) // 2
        self.pinky_spawn = (spawn_x_pky, spawn_y_pky)
        self.pinky = Pinky(
            spawn_x_pky, spawn_y_pky, pac_sheet, GAME_WIDTH, GAME_HEIGHT)

        # Clyde
        self.clyde_spawn = (0, 0)
        self.clyde = Clyde(
            0, 0, pac_sheet, GAME_WIDTH, GAME_HEIGHT)

        # Inky
        spawn_x_inky = (len(mazegen.maze[0]) - 1) * 50 + (
                50 - PacSpriteSheet.SPRITE_W) // 2
        spawn_y_inky = (50 - PacSpriteSheet.SPRITE_H) // 2
        self.inky_spawn = (spawn_x_inky, spawn_y_inky)
        self.inky = Inky(
            spawn_x_inky, spawn_y_inky, pac_sheet, GAME_WIDTH, GAME_HEIGHT)

        self.start_game()

    def start_game(self) -> None:
        """create maze, check user inputs and render new elements"""
        self.paused = False
        while self.running:
            self.update()
            self.time -= self.clock.tick(60) / 1000
            self.time = round(self.time, 2)
            self.render(mazegen)
            if self.time <= 0:
                self.time = 0
                self.running = False
                self.menus.over_menu()

    def sort_score_file(self) -> None:
        with open(configuration.highscore_filename, 'r') as f:
            txt = f.read()
        scores_list = txt.split("\n")
        scores_dict = {}

        for line in scores_list:
            temp = line.split(": ")
            if len(temp) < 2:
                break
            scores_dict.update({temp[0]: int(temp[1])})

        scores_dict = dict(
            sorted(scores_dict.items(),
                   key=lambda item: item[1], reverse=True))
        with open(configuration.highscore_filename, 'w') as f:
            for name, score in scores_dict.items():
                f.write(
                    f"{name}: {score}\n")

    def quit_game_over(self) -> None:
        with open(configuration.highscore_filename, 'a') as f:
            f.write(
                f"{self.looser.get_value()}: {self.pacgums.score}\n")
        self.sort_score_file()
        pygame.quit()
        quit()

    def check_collisions(self) -> None:
        if self.invulnerable_timer > 0:
            self.invulnerable_timer -= 1
            return

        HIT_MARGIN = 12
        hit_w = PacSpriteSheet.SPRITE_W - HIT_MARGIN * 2
        hit_h = PacSpriteSheet.SPRITE_H - HIT_MARGIN * 2

        pac_rect = pygame.Rect(self.pacwoman.x + HIT_MARGIN,
                               self.pacwoman.y + HIT_MARGIN,
                               hit_w, hit_h)

        ghosts = {
            "blinky": (self.blinky, self.blinky_spawn),
            "inky": (self.inky, self.inky_spawn),
            "pinky": (self.pinky, self.pinky_spawn),
            "clyde": (self.clyde, self.clyde_spawn)
        }

        for name, (ghost, spawn) in ghosts.items():
            ghost_rect = pygame.Rect(
                                     ghost.x + HIT_MARGIN, ghost.y + HIT_MARGIN,
                                     hit_w, hit_h)
            if pac_rect.colliderect(ghost_rect):
                if self.pacgums.eat_ghosts:
                    ghost.x, ghost.y = spawn
                    self.pacgums.score += 200
                else:
                    self.pacwoman_hit()
                    return

    def pacwoman_hit(self):
        self.lives -= 1
        if self.lives <= 0:
            self.running = False
            self.menus.over_menu()
        else:
            self.respawn_all()

    def respawn_all(self):
        self.pacwoman.x, self.pacwoman.y = self.pacwoman_spawn
        self.pacwoman.state = "idle"

        self.blinky.x, self.blinky.y = self.blinky_spawn
        self.pinky.x, self.pinky.y = self.pinky_spawn
        self.clyde.x, self.clyde.y = self.clyde_spawn
        self.inky.x, self.inky.y = self.inky_spawn


        self.invulnerable_timer = 90


if __name__ == "__main__":
    configuration = parse()
    game = GameController()
    game.set_background()
    mazegen = mazegenerator.MazeGenerator()

    # start from starting menu
    game.menus.start_menu()