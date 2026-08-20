import pygame  # type: ignore
from pygame_menu import widgets  # type: ignore
# import random
from mazegenerator import MazeGenerator  # type: ignore
from parsing import parse
from pacwoman import PacSpriteSheet, Pacwoman
from ghosts import Blinky, Pinky, Clyde, Inky
from pacgums import Pacgums
from typing import Callable, Any
from functools import partial


MAZE_CELL = 50
MAZE_COLS = 15
MAZE_ROWS = 15
GUI_HEIGHT = 80

GAME_WIDTH = MAZE_COLS * MAZE_CELL + 1
GAME_HEIGHT = MAZE_ROWS * MAZE_CELL + 1
SCREENWIDTH = GAME_WIDTH
SCREENHEIGHT = GUI_HEIGHT + GAME_HEIGHT
SCREENSIZE = (SCREENWIDTH, SCREENHEIGHT)

BLACK = (0, 0, 0)
PINK = (255, 209, 220)


class GameController(object):
    def __init__(self) -> None:
        # prevent circular import in menu.py:
        from menu import Gamemenus

        pygame.init()
        self.screen = pygame.display.set_mode(SCREENSIZE, 0, 32)
        self.game_surface = self.screen.subsurface(
            pygame.Rect(0, GUI_HEIGHT, GAME_WIDTH, GAME_HEIGHT))
        self.background: pygame.surface.Surface = None
        self.running = False
        self.ghost_state = "normal"
        self.over = False
        self.looser: widgets.TextInput = None
        self.pac_sheet = PacSpriteSheet("sprites/pac_sheet.png")
        self.pacgums = Pacgums(
            self.pac_sheet, gum_row=5, gum_col=8, sp_gum_row=6, sp_gum_col=8)
        self.menus = Gamemenus(self)
        self.scatter_duration: float = 6.0
        self.scatter_timer: float = 0.0
        self.time_interval_scatter = 40000  # 40 seconds (keeps running during
        # the 6 seconds of scatter mode so actually 34 seconds)
        self.scatter_event = pygame.USEREVENT+1
        self.pacwoman_invincible = True
        pygame.time.set_timer(self.scatter_event, self.time_interval_scatter)

    def set_background(self) -> None:
        self.background = pygame.Surface(SCREENSIZE).convert()
        self.background.fill(BLACK)

    def update(self) -> None:
        """function called once per frame of the game == our game loop
        call the function that checks the user inputs, and makes the ghosts
        move
        """
        self.check_events()
        dt: float = self.clock.get_time() / 1000

        if self.game_state == "dying":
            self.pacwoman.update()
            if self.pacwoman.is_death_animation_done():
                self.respawn_all()
                self.game_state = "frozen"
                self.respawn_timer = self.respawn_delay
            return

        if self.game_state == "frozen":
            self.respawn_timer -= dt
            if self.respawn_timer <= 0:
                self.game_state = "playing"
            return

        keys: pygame.key.ScancodeWrapper = pygame.key.get_pressed()
        self.pacwoman.input(keys)
        self.pacwoman.move(mazegen)
        self.pacwoman.update()
        self.pacgums.eat(self.pacwoman)
        self.pacgums.update(dt)

        if not self.pacgums.gums and not self.pacgums.super_gum:
            self.win_game()

        pellet_just_activate = (
            self.pacgums.eat_ghosts and not self.prev_eat_ghosts)
        self.prev_eat_ghosts = self.pacgums.eat_ghosts

        for ghost in (self.blinky, self.inky, self.clyde, self.pinky):
            if pellet_just_activate and not ghost.dead:
                ghost.scared = True
            if not self.pacgums.eat_ghosts:
                ghost.scared = False
            if self.ghost_state != "scared" and ghost.scared:
                self.ghost_state = "scared"
            ghost.warning = (
                self.pacgums.eat_ghosts and self.pacgums.scared_timer <= 4)

        if self.ghost_state == "scatter":
            self.scatter_timer -= dt
            if self.scatter_timer <= 0:
                self.ghost_state = "normal"
                self.scatter_timer = 0.0

        if self.blinky.dead:
            self.blinky.scatter_move(
                mazegen, self.blinky_spawn[0], self.blinky_spawn[1])
        else:
            self.blinky_move: dict[str, Callable[..., Any]] = {
                "normal": partial(
                    self.blinky.bfs_move, mazegen, self.pacwoman),
                "scatter": partial(
                    self.blinky.scatter_move, mazegen, self.blinky_spawn[0],
                    self.blinky_spawn[1]),
                "scared": partial(
                    self.blinky.bfs_move, mazegen, self.pacwoman),
                # "scared": partial(
                #   self.blinky.scared_move, mazegen, self.pacwoman)
                }
            self.blinky_move[self.ghost_state]()
        self.blinky.update()

        if self.pinky.dead:
            self.pinky.scatter_move(
                mazegen, self.pinky_spawn[0], self.pinky_spawn[1])
        self.pinky_move: dict[str, Callable[..., Any]] = {
            "normal": partial(self.pinky.move_random, mazegen),
            "scatter": partial(
                self.pinky.scatter_move, mazegen, self.pinky_spawn[0],
                self.pinky_spawn[1]),
            "scared": partial(self.pinky.move_random, mazegen),
            # "scared": partial(
            #     self.pinky.scared_move, mazegen, self.pacwoman)
            }
        self.pinky_move[self.ghost_state]()
        self.pinky.update()

        if self.clyde.dead:
            self.clyde.scatter_move(
                mazegen, self.clyde_spawn[0], self.clyde_spawn[1])
        self.clyde_move: dict[str, Callable[..., Any]] = {
            "normal": partial(self.clyde.move_random, mazegen),
            "scatter": partial(
                self.clyde.scatter_move, mazegen, self.clyde_spawn[0],
                self.clyde_spawn[1]),
            "scared": partial(self.clyde.move_random, mazegen),
            # "scared": partial(
            #     self.clyde.scared_move, mazegen, self.pacwoman)
            }
        self.clyde_move[self.ghost_state]()
        self.clyde.update()

        if self.inky.dead:
            self.inky.scatter_move(
                mazegen, self.inky_spawn[0], self.inky_spawn[1])
        self.inky_move: dict[str, Callable[..., Any]] = {
            "normal": partial(self.inky.move_random, mazegen),
            "scatter": partial(
                self.inky.scatter_move, mazegen, self.inky_spawn[0],
                self.inky_spawn[1]),
            "scared": partial(self.inky.move_random, mazegen),
            # "scared": partial(
            #     self.inky.scared_move, mazegen, self.pacwoman)
            }
        self.inky_move[self.ghost_state]()
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
            if (event.type == self.scatter_event
               and self.ghost_state == "normal"):
                self.ghost_state = "scatter"
                self.scatter_timer = self.scatter_duration

    def render(self, mazegen: MazeGenerator) -> None:
        """draw images to the screen"""
        # draw background
        self.screen.fill(BLACK, pygame.Rect(0, 0, SCREENWIDTH, GUI_HEIGHT))
        self.game_surface.fill(BLACK)
        # draw interface (score, lives, etc)
        score_text = self.score_font.render(
            f'Score: {self.pacgums.score}', True, (255, 255, 255))
        self.screen.blit(score_text, (10, 10))
        timer_text = self.timer_font.render(
            f'Time: {int(self.time)}', True, (255, 255, 255))
        self.screen.blit(timer_text, (10, 50))

        self.draw_maze(mazegen)
        self.pacgums.draw(self.game_surface)
        self.pacwoman.draw(self.game_surface)

        if self.game_state != "dying":
            self.blinky.draw(self.game_surface)
            self.pinky.draw(self.game_surface)
            self.clyde.draw(self.game_surface)
            self.inky.draw(self.game_surface)

        # update display with changes
        pygame.display.flip()

    def draw_maze(self, mazegen: MazeGenerator) -> None:
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
                        self.game_surface, PINK, (cx + 50, cy), (
                            cx + 50, cy + 50))
                # South
                if cell & 4:
                    pygame.draw.line(
                        self.game_surface, PINK, (cx, cy + 50), (
                            cx + 50, cy + 50))
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
        self.time = 220.0
        self.running = True
        self.lives = 3
        self.ghost_state = "normal"
        self.invulnerable_timer = 0
        self.prev_eat_ghosts = False
        self.score_font = pygame.font.Font(None, 36)
        self.timer_font = pygame.font.Font(None, 36)
        self.game_state = "playing"
        self.respawn_delay = 2.0
        self.respawn_timer = 0.0
        self.won = False
        pac_sheet = self.pac_sheet

        # Pacwoman
        maze_width = len(mazegen.maze[0])
        maze_height = len(mazegen.maze)
        center_col: int = maze_width // 2
        center_row: int = maze_height // 2
        spawn_x: int = center_col * 50 + (50 - PacSpriteSheet.SPRITE_W) // 2
        spawn_y: int = center_row * 50 + (50 - PacSpriteSheet.SPRITE_H) // 2
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
            sorted(
                scores_dict.items(), key=lambda item: item[1], reverse=True))
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

        pac_rect = pygame.Rect(
            self.pacwoman.x + HIT_MARGIN,
            self.pacwoman.y + HIT_MARGIN,
            hit_w, hit_h)

        self.ghosts = {
            "blinky": (self.blinky, self.blinky_spawn),
            "inky": (self.inky, self.inky_spawn),
            "pinky": (self.pinky, self.pinky_spawn),
            "clyde": (self.clyde, self.clyde_spawn)
        }

        for name, (ghost, spawn) in self.ghosts.items():
            ghost_rect = pygame.Rect(
                ghost.x + HIT_MARGIN, ghost.y + HIT_MARGIN, hit_w, hit_h)
            if pac_rect.colliderect(ghost_rect):
                if ghost.scared:
                    ghost.dead = True
                    ghost.update()
                    self.pacgums.score += 200
                elif not self.pacwoman_invincible:
                    self.pacwoman_hit()
                    return
                elif ghost.dead:
                    pass

    def win_game(self) -> None:
        self.running = False
        self.won = True
        self.menus.over_menu()

    def pacwoman_hit(self) -> None:
        self.lives -= 1
        if self.lives <= 0:
            self.running = False
            self.won = False
            self.menus.over_menu()
        else:
            self.pacwoman.start_death_animation()
            self.game_state = "dying"

    def save_score(self, name: str) -> None:
        with open(configuration.highscore_filename, 'a') as f:
            f.write(f"{name}: {self.pacgums.score}\n")
        self.sort_score_file()

    def get_top_scores(self, limit: int = 10) -> list[tuple[str, int]]:
        scores: list[tuple[str, int]] = []
        try:
            with open(configuration.highscore_filename, 'r') as f:
                for line in f:
                    parts = line.strip().split(": ")
                    if len(parts) == 2:
                        scores.append((parts[0], int(parts[1])))
        except FileNotFoundError:
            pass
        return scores[:limit]

    def quit_game_over(self) -> None:
        self.save_score(self.looser.get_value())
        pygame.quit()
        quit()

    def respawn_all(self) -> None:
        self.pacwoman.x, self.pacwoman.y = self.pacwoman_spawn
        self.pacwoman.state = "idle"
        self.pacwoman.direction = (1, 0)
        self.pacwoman.next_direction = (1, 0)
        self.pacwoman.frame_index = 0
        self.pacwoman.current_frame = self.pacwoman.frame_sets[(1, 0)][0]

        self.blinky.x, self.blinky.y = self.blinky_spawn
        self.pinky.x, self.pinky.y = self.pinky_spawn
        self.clyde.x, self.clyde.y = self.clyde_spawn
        self.inky.x, self.inky.y = self.inky_spawn

        self.invulnerable_timer = 90


if __name__ == "__main__":
    configuration = parse()
    game = GameController()
    game.set_background()
    mazegen = MazeGenerator()

    # start from starting menu
    game.menus.start_menu()
