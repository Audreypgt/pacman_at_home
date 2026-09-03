
import os
from functools import partial
from typing import Callable, Any
from random import randint

import pygame
import pygame_menu
from pygame_menu import themes
from pygame_menu.widgets.widget.textinput import TextInput

from pacwoman import PacSpriteSheet, Pacwoman
from mazegenerator import MazeGenerator
from ghosts import Blinky, Pinky, Clyde, Inky, Ghosts
from pacgums import Pacgums
from parsing import Configuration


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
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)

WALL_WIDTH = 12
WALL_INNER_WIDTH = 4

SPRITES_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "sprites")

PAC_YELLOW = (255, 242, 0)
PAC_PINK = (255, 100, 175)
PAC_DARK = (10, 15, 45)
PAC_GHOST = (60, 70, 130)
PAC_WHITE = (245, 245, 250)


def pacwoman_theme(width: int = 600, height: int = 700) -> themes.Theme:
    """Custom theme that matches the PacWoman game aesthetic."""
    return themes.Theme(
        background_color=PAC_DARK,
        title_background_color=PAC_PINK,
        title_font_color=PAC_DARK,
        title_font=pygame_menu.font.FONT_FRANCHISE,
        widget_font=pygame_menu.font.FONT_OPEN_SANS,
        widget_font_color=PAC_WHITE,
        widget_font_size=22,
        title_font_size=44,
        widget_margin=(0, 12),
        widget_padding=(10, 8),
        selection_color=PAC_YELLOW,
        cursor_color=PAC_PINK,
        scrollbar_color=PAC_PINK,
        scrollbar_slider_color=PAC_YELLOW,
    )


class GameController(object):
    def __init__(self, configuration: Configuration) -> None:
        self.configuration: Configuration = configuration
        self.mazegen: MazeGenerator = MazeGenerator((MAZE_COLS, MAZE_ROWS))

        self.level_seeds = {
            1: configuration.levels["level_1"].seed,
            2: randint(0, 999),
            3: randint(0, 999),
            4: randint(0, 999),
            5: randint(0, 999),
            6: randint(0, 999),
            7: randint(0, 999),
            8: randint(0, 999),
            9: randint(0, 999),
            10: randint(0, 999)}

        pygame.init()
        self.screen = pygame.display.set_mode(SCREENSIZE, 0, 32)
        self.game_surface = self.screen.subsurface(
            pygame.Rect(0, GUI_HEIGHT, GAME_WIDTH, GAME_HEIGHT))
        self.background: pygame.surface.Surface | None = None
        self.maze_surface: pygame.surface.Surface | None = None
        self.running = False
        self.scatter = False
        self.over = False
        self.won = False
        self.prev_eat_ghosts: bool = False
        self.game_state: str = ""
        self.respawn_delay = 0.0
        self.time = 0.0
        self.lives: int = configuration.lives
        self.player: TextInput | None = None
        self.ghosts: dict[str, tuple[Ghosts, tuple[int, int]]] = {}
        self.dict_scores: dict[str, int] = {}
        self.sprite_w = 42
        self.sprite_h = 42
        self.pac_sheet = PacSpriteSheet(
            "sprites/pac_sheet.png",
            sprite_w=self.sprite_w, sprite_h=self.sprite_h)
        self.pacgums = Pacgums(
            self.pac_sheet, gum_row=5, gum_col=8, sp_gum_row=6, sp_gum_col=8)
        self.menus = Gamemenus(self)
        self.scatter_duration: float = 6.0
        self.scatter_timer: float = 0.0
        self.time_interval_scatter: float = 40.0
        self.current_level = 1
        self.max_level = max(self.level_seeds.keys())
        self.cheat_invincible = False
        self.cheat_freeze_time = False
        self.beat_the_game = False

    def set_background(self) -> None:
        self.background = pygame.Surface(SCREENSIZE).convert()
        self.background.fill(BLACK)

    def update(self) -> None:
        """function called once per frame of the game == our game loop
        call the function that checks the user inputs, and makes the ghosts
        move
        """
        # Cap dt so a long pause (or any blocking menu) can't drain the
        # timer all at once on the first frame after we resume.
        dt: float = min(self.clock.get_time() / 1000, 0.1)

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

        if not self.cheat_freeze_time:
            self.time = round(self.time - dt, 2)
            if self.time <= 0:
                self.time = 0
                self.running = False
                self.won = False
                self.menus.over_menu()
                return

        self.check_events()

        if self.time_interval_scatter > 0:
            self.time_interval_scatter = round(
                self.time_interval_scatter - dt, 2)
        else:
            self.time_interval_scatter = 40.0

        if self.time_interval_scatter <= 0:
            self.scatter = True
            self.scatter_timer = self.scatter_duration

        keys: pygame.key.ScancodeWrapper = pygame.key.get_pressed()
        self.pacwoman.input(keys)
        self.pacwoman.move(self.mazegen)
        self.pacwoman.update()
        self.pacgums.eat(self.pacwoman, self.configuration)
        self.pacgums.update(dt)

        pellet_just_activate = (
            self.pacgums.eat_ghosts and not self.prev_eat_ghosts)
        self.prev_eat_ghosts = self.pacgums.eat_ghosts

        for _, (ghost, _) in self.ghosts.items():
            if pellet_just_activate and not ghost.dead:
                ghost.scared = True
            if not self.pacgums.eat_ghosts:
                ghost.scared = False
            if ghost.ghost_state != "scared" and ghost.scared:
                ghost.ghost_state = "scared"
            elif ghost.ghost_state == "scared" and not ghost.scared:
                ghost.ghost_state = "normal"
            ghost.warning = (
                self.pacgums.eat_ghosts and self.pacgums.scared_timer <= 4)

        if self.scatter:
            for _, (ghost, _) in self.ghosts.items():
                if ghost.ghost_state == "normal":
                    ghost.ghost_state = "scatter"
            self.scatter_timer -= dt
            if self.scatter_timer <= 0:
                for _, (ghost, _) in self.ghosts.items():
                    ghost.ghost_state = "normal"
                self.scatter_timer = 0.0
                self.scatter = False

        for name, (ghost, spawn) in self.ghosts.items():
            if ghost.dead:
                ghost.ghost_state = "normal"
                ghost.scatter_move(
                    self.mazegen, spawn[0], spawn[1])
            else:
                self.ghost_move: dict[str, Callable[..., Any]] = {
                    "blinky": partial(
                        self.blinky.bfs_move, self.mazegen, self.pacwoman),
                    "inky": partial(
                        self.inky.inky_move, self.mazegen, self.pacwoman),
                    "pinky": partial(
                        self.pinky.bfs_move, self.mazegen, self.pacwoman),
                    "clyde": partial(
                        self.clyde.clyde_move, self.mazegen, self.pacwoman,
                        spawn[0], spawn[1]),
                    "scatter": partial(
                        ghost.scatter_move, self.mazegen, spawn[0],
                        spawn[1]),
                    "scared": partial(
                        ghost.move_random, self.mazegen)}
                if ghost.ghost_state != "normal":
                    self.ghost_move[ghost.ghost_state]()
                else:
                    self.ghost_move[name]()
                ghost.update()

        self.check_collisions()

        if not self.pacgums.gums and not self.pacgums.super_gum:
            self.level_complete()

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
                if event.key == pygame.K_i:
                    self.cheat_invincible = not self.cheat_invincible
                if event.key == pygame.K_p:
                    self.cheat_freeze_time = not self.cheat_freeze_time
                if event.key == pygame.K_n:
                    if self.current_level < self.max_level:
                        self.running = False
                        self.next_level()
                        return
                    # On the last level: N acts like winning the level
                    self.running = False
                    self.level_complete()
                    return

    def render(self) -> None:
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

        level_text = self.score_font.render(
            f'Level: {self.current_level}', True, (255, 255, 255))
        self.screen.blit(level_text, (SCREENWIDTH - 250, 10))

        lives_text = self.lives_font.render(f"Remaining Lives: {self.lives}",
                                            True, (255, 255, 255))
        self.screen.blit(lives_text, (SCREENWIDTH - 250, 50))

        cheat_labels = []
        if self.cheat_invincible:
            cheat_labels.append("INVINCIBLE")
        if self.cheat_freeze_time:
            cheat_labels.append("TIME FROZEN")
        if cheat_labels:
            cheat_text = self.timer_font.render(
                " | ".join(cheat_labels), True, YELLOW)
            self.screen.blit(cheat_text, cheat_text.get_rect(
                topright=(SCREENWIDTH - 250, 50)))

        # draw maze, gums and sprites
        self.draw_maze()
        self.pacgums.draw(self.game_surface)
        self.pacwoman.draw(self.game_surface)

        if self.game_state != "dying":
            self.blinky.draw(self.game_surface)
            self.pinky.draw(self.game_surface)
            self.clyde.draw(self.game_surface)
            self.inky.draw(self.game_surface)

        # update display with changes
        pygame.display.flip()

    def get_wall_segments(self) -> list[tuple[
            tuple[int, int], tuple[int, int]]]:
        """collect every wall edge of the maze as line segments"""
        segments: list[tuple[tuple[int, int], tuple[int, int]]] = []
        cy = 0
        for line in self.mazegen.maze:
            cx = 0
            for cell in line:
                # North
                if cell & 1:
                    segments.append(((cx, cy), (cx + 50, cy)))
                # East
                if cell & 2:
                    segments.append(((cx + 50, cy), (cx + 50, cy + 50)))
                # South
                if cell & 4:
                    segments.append(((cx, cy + 50), (cx + 50, cy + 50)))
                # West
                if cell & 8:
                    segments.append(((cx, cy), (cx, cy + 50)))
                cx += 50
            cy += 50

        # 1 = 0001 Nord
        # 2 = 0010 Est
        # 4 = 0100 Sud
        # 8 = 1000 Ouest
        # 3 = 0011 Fermee au Nord et a l'Est
        # 15 = 1111 tout ferme
        return segments

    def draw_capsule(
            self, surface: pygame.surface.Surface,
            color: tuple[int, int, int],
            seg: tuple[tuple[int, int], tuple[int, int]],
            width: int) -> None:
        (x1, y1), (x2, y2) = seg
        r = width // 2
        if y1 == y2:
            rect = pygame.Rect(min(x1, x2), y1 - r, abs(x2 - x1), width)
        else:
            rect = pygame.Rect(x1 - r, min(y1, y2), width, abs(y2 - y1))
        pygame.draw.rect(surface, color, rect)
        pygame.draw.circle(surface, color, (x1, y1), r)
        pygame.draw.circle(surface, color, (x2, y2), r)

    def build_maze_surface(self) -> None:
        surface = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
        segments = self.get_wall_segments()

        # thick pink skeleton
        for seg in segments:
            self.draw_capsule(surface, PINK, seg, WALL_WIDTH)

        # black inner layer, thinner, to hollow out the wall
        for seg in segments:
            self.draw_capsule(surface, BLACK, seg, WALL_INNER_WIDTH)

        self.maze_surface = surface

    def draw_maze(self) -> None:
        if self.maze_surface is None:
            self.build_maze_surface()
        if self.maze_surface:
            maze_temp: pygame.surface.Surface = self.maze_surface
            self.game_surface.blit(maze_temp, (0, 0))

    def set_up_game(self) -> None:
        self.time_interval_scatter = 40.0
        self.current_level = 1
        self.load_level(reset_progress=True)
        self.cheat_invincible = False
        self.cheat_freeze_time = False
        self.beat_the_game = False

    def restart_game(self) -> None:
        self.set_up_game()

    def next_level(self) -> None:
        self.current_level += 1
        self.load_level(reset_progress=False)

    def level_complete(self) -> None:
        self.running = False
        self.won = True
        if self.current_level >= self.max_level:
            self.beat_the_game = True
        self.menus.over_menu()

    def load_level(self, reset_progress: bool) -> None:
        if self.over and self.won and self.current_level == self.max_level:
            with open(self.configuration.highscore_filename, 'a') as f:
                if self.player:
                    f.write(
                        f"{self.player.get_value()}: {self.pacgums.score}\n")
            self.sort_score_file()
            self.over = False
        self.clock = pygame.time.Clock()
        self.time = self.configuration.lvl_max_time
        self.time_interval_scatter = 40.0
        self.running = True
        self.won = False
        self.invulnerable_timer = 0
        self.prev_eat_ghosts = False
        self.score_font = pygame.font.Font(None, 36)
        self.timer_font = pygame.font.Font(None, 36)
        self.lives_font = pygame.font.Font(None, 36)
        self.game_state = "playing"
        self.respawn_delay = 2.0
        self.respawn_timer = 0.0
        pac_sheet = self.pac_sheet

        if reset_progress:
            self.lives = self.configuration.lives
        saved_score = self.pacgums.score
        self.mazegen.generate(self.level_seeds[self.current_level])
        # to reset the walls between each levels, so that in level 2 you dont
        # get level 1 walls, its cache.
        self.maze_surface = None

        # Pacwoman
        maze_width = len(self.mazegen.maze[0])
        maze_height = len(self.mazegen.maze)
        center_col: int = maze_width // 2
        center_row: int = maze_height // 2
        spawn_x: int = center_col * 50 + (50 - self.sprite_w) // 2
        spawn_y: int = center_row * 50 + (50 - self.sprite_h) // 2
        self.pacwoman_spawn = (spawn_x, spawn_y)
        self.pacwoman: Pacwoman = Pacwoman(
            spawn_x, spawn_y, pac_sheet, GAME_WIDTH, GAME_HEIGHT)

        self.pacgums.init_gums(
            self.mazegen, self.pacwoman, self.current_level,
            self.configuration)
        if not reset_progress:
            self.pacgums.score = saved_score

        # Blinky
        spawn_x_blky = (
            len(self.mazegen.maze[0]) - 1) * 50 + (
                50 - self.sprite_w) // 2
        spawn_y_blky = (
            len(self.mazegen.maze) - 1) * 50 + (
                50 - self.sprite_h) // 2
        self.blinky_spawn = (spawn_x_blky, spawn_y_blky)
        self.blinky: Blinky = Blinky(
            spawn_x_blky, spawn_y_blky, pac_sheet,
            GAME_WIDTH, GAME_HEIGHT)

        # Pinky
        spawn_x_pky = (50 - self.sprite_w) // 2
        spawn_y_pky = (
            len(self.mazegen.maze) - 1) * 50 + (
                50 - self.sprite_h) // 2
        self.pinky_spawn = (spawn_x_pky, spawn_y_pky)
        self.pinky: Pinky = Pinky(
            spawn_x_pky, spawn_y_pky, pac_sheet, GAME_WIDTH, GAME_HEIGHT)

        # Clyde
        self.clyde_spawn = (0, 0)
        self.clyde: Clyde = Clyde(
            0, 0, pac_sheet, GAME_WIDTH, GAME_HEIGHT)

        # Inky
        spawn_x_inky = (len(self.mazegen.maze[0]) - 1) * 50 + (
            50 - self.sprite_w) // 2
        spawn_y_inky = (50 - self.sprite_h) // 2
        self.inky_spawn = (spawn_x_inky, spawn_y_inky)
        self.inky: Inky = Inky(
            spawn_x_inky, spawn_y_inky, pac_sheet, GAME_WIDTH, GAME_HEIGHT)

        self.ghosts = {
            "blinky": (self.blinky, self.blinky_spawn),
            "inky": (self.inky, self.inky_spawn),
            "pinky": (self.pinky, self.pinky_spawn),
            "clyde": (self.clyde, self.clyde_spawn)
        }
        for _, (ghost, _) in self.ghosts.items():
            ghost.ghost_state = "normal"

        self.start_game()

    def start_game(self) -> None:
        """set clock, update game, check user inputs and render new elements"""
        self.paused = False
        # Reset the clock so the first update() after a long pause
        # doesn't see a huge dt and drain the timer.
        self.clock.tick()
        while self.running:
            self.update()
            self.clock.tick(60)
            self.render()

    def sort_score_file(self) -> None:
        with open(self.configuration.highscore_filename, 'r') as f:
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
        with open(self.configuration.highscore_filename, 'w') as f:
            for name, score in scores_dict.items():
                f.write(
                    f"{name}: {score}\n")

    def check_collisions(self) -> None:
        if self.invulnerable_timer > 0:
            self.invulnerable_timer -= 1
            return

        HIT_MARGIN = 12
        hit_w = self.sprite_w - HIT_MARGIN * 2
        hit_h = self.sprite_h - HIT_MARGIN * 2

        pac_rect = pygame.Rect(
            self.pacwoman.x + HIT_MARGIN,
            self.pacwoman.y + HIT_MARGIN,
            hit_w, hit_h)

        for name, (ghost, spawn) in self.ghosts.items():
            ghost_rect = pygame.Rect(
                ghost.x + HIT_MARGIN, ghost.y + HIT_MARGIN, hit_w, hit_h)
            if pac_rect.colliderect(ghost_rect):
                if ghost.scared:
                    ghost.dead = True
                    ghost.update()
                    ghost.scared = False
                    self.pacgums.score += self.configuration.points_per_ghost
                elif ghost.dead:
                    pass
                elif self.cheat_invincible:
                    pass
                else:
                    self.pacwoman_hit()
                    return

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
        if len(name) > 9:
            short_name = ""
            for i, letter in enumerate(name, start=1):
                if i == 10:
                    break
                short_name += str(letter)
            name = short_name
            print(short_name)
            print(name)

        try:
            self.dict_scores[name]
            score_1 = self.dict_scores[name]
            score_2 = self.pacgums.score
            if score_1 > score_2:
                return
        except KeyError:
            with open(self.configuration.highscore_filename, 'a') as f:
                f.write(f"{name}: {self.pacgums.score}\n")
            self.dict_scores.update({name: self.pacgums.score})
            self.sort_score_file()

    def get_top_scores(self, limit: int = 10) -> list[tuple[str, int]]:
        scores: list[tuple[str, int]] = []
        try:
            with open(self.configuration.highscore_filename, 'r') as f:
                for line in f:
                    parts = line.strip().split(": ")
                    if len(parts) == 2:
                        scores.append((parts[0], int(parts[1])))
        except FileNotFoundError:
            pass
        return scores[:limit]

    def quit_game_over(self) -> None:
        if self.won and self.current_level == self.max_level and self.player:
            self.save_score(self.player.get_value())
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
        self.time_interval_scatter = 40.0


class Gamemenus:
    def __init__(self, game: GameController):
        self.game = game
        self.logo = "sprites/pacwoman_logo.png"
        self.num_frames = 41
        self.sprite_w = 322
        self.sprite_h = 119
        sheet_w = self.sprite_w * self.num_frames
        sheet_h = self.sprite_h
        self.control_sheet = PacSpriteSheet(
            os.path.join(SPRITES_DIR, "control_sheet.png"),
            sprite_w=sheet_w, sprite_h=sheet_h,
        )
        full = self.control_sheet.get_sprite_at(0, 0, sheet_w, sheet_h)
        self.controls_frames: list[pygame.Surface] = [
            full.subsurface((i * self.sprite_w, 0,
                             self.sprite_w, self.sprite_h))
            for i in range(self.num_frames)
        ]
        self.controls_frame_index = 0
        self.controls_animation_speed = 1.5
        self.controls_timer = 0
        self.current_controls_frame = self.controls_frames[0]
        self.started_menu = False
        self.paused_menu = False
        self.ldbd_menu = False

    def update(self) -> None:
        self.controls_timer += 1
        if self.controls_timer >= self.controls_animation_speed:
            self.controls_timer = 0
            self.controls_frame_index = (
                (self.controls_frame_index + 1) % len(self.controls_frames)
            )
            self.current_controls_frame = self.controls_frames[
                self.controls_frame_index
            ]

    def start_menu(self) -> None:
        main_menu = pygame_menu.Menu(
            "", SCREENWIDTH, SCREENHEIGHT,
            theme=pacwoman_theme(SCREENWIDTH, SCREENHEIGHT))
        main_menu.add.image(self.logo)
        main_menu.add.button("Play", self.game.set_up_game)
        main_menu.add.button("Instructions", self.instructions_menu)
        main_menu.add.button("Leaderboard", self.leaderboard_menu)
        main_menu.add.button("Quit", pygame_menu.events.EXIT)
        main_menu.mainloop(self.game.screen)

    def pause_menu(self) -> None:
        pause_menu = pygame_menu.Menu(
            "", SCREENWIDTH, SCREENHEIGHT,
            theme=pacwoman_theme(SCREENWIDTH, SCREENHEIGHT))
        pause_menu.add.image(self.logo)
        pause_menu.add.button("Resume", self.game.start_game)
        pause_menu.add.button("Restart", self.game.restart_game)
        pause_menu.add.button("Main Menu", self.start_menu)
        pause_menu.add.button("Quit", pygame_menu.events.EXIT)
        pause_menu.mainloop(self.game.screen)

    def over_menu(self) -> None:
        self.game.over = True
        title = "You Win!" if self.game.won else "Game Over"

        over_menu = pygame_menu.Menu(
            "", SCREENWIDTH, SCREENHEIGHT,
            theme=pacwoman_theme(SCREENWIDTH, SCREENHEIGHT))
        over_menu .add.image(self.logo)
        over_menu.add.label(title)
        over_menu.add.label(f"Score: {self.game.pacgums.score}")

        # if self.game.won and self.game.current_level == self.game.max_level:
        self.game.player = over_menu.add.text_input(
            "Name: ", default="Player")
        over_menu.add.button(
            "Save & View Leaderboard",
            lambda: self.leaderboard_menu(save_current=True),
        )
        if self.game.won and self.game.current_level < self.game.max_level:
            over_menu.add.button("Next Level", self.game.next_level)

        if not self.game.won:
            over_menu.add.button("Need a hand ?", self.cheat_menu)

        over_menu.add.button("Restart", self.game.restart_game)
        over_menu.add.button(
            "Quit", self.game.quit_game_over)
        over_menu.mainloop(self.game.screen)

    def cheat_menu(self) -> None:
        cheat_menu = pygame_menu.Menu(
            "", SCREENWIDTH, SCREENHEIGHT,
            theme=pacwoman_theme(SCREENWIDTH, SCREENHEIGHT))
        cheat_menu .add.image(self.logo)
        cheat_menu.add.label("Cheat codes:")
        cheat_menu.add.label("Press i to be invicible")
        cheat_menu.add.label("Press p to freeze time")
        cheat_menu.add.button("Back", self.over_menu)
        cheat_menu.mainloop(self.game.screen)

    def leaderboard_menu(self, save_current: bool = False) -> None:
        if save_current:
            if self.game.player:
                self.game.save_score(self.game.player.get_value())

        board_menu = pygame_menu.Menu(
            "", SCREENWIDTH, SCREENHEIGHT,
            theme=pacwoman_theme(SCREENWIDTH, SCREENHEIGHT))
        top_scores = self.game.get_top_scores()
        board_menu.add.image(self.logo)
        board_menu.add.label("Top 10 Scores")
        if not top_scores:
            board_menu.add.label("No scores yet")
        for i, (name, score) in enumerate(top_scores, start=1):
            board_menu.add.label(f"{i}. {name}: {score}")

        if self.game.won and self.game.current_level < self.game.max_level:
            board_menu.add.button("Next Level", self.game.next_level)
        board_menu.add.button("Main Menu", self.start_menu)
        board_menu.add.button("Quit", pygame_menu.events.EXIT)
        board_menu.mainloop(self.game.screen)

    def instructions_menu(self) -> None:
        instructions_page = pygame_menu.Menu(
            "", SCREENWIDTH, SCREENHEIGHT,
            theme=pacwoman_theme(SCREENWIDTH, SCREENHEIGHT))

        # instructions_page.add.image(self.logo, scale=(0.4, 0.4))
        instructions_page.add.vertical_margin(20)
        instructions_page.add.label("How to Play:")
        instructions_page.add.vertical_margin(self.sprite_h)
        instructions_page.add.label("Move with the arrow keys")
        instructions_page.add.label("Eat all pacgums to win")
        instructions_page.add.label("Avoid the ghosts!")
        instructions_page.add.label("Super PacGums let you eat ghosts")
        instructions_page.add.vertical_margin(70)
        instructions_page.add.button("Back", self.start_menu)

        def advance_frame() -> None:
            self.update()
            x = (self.game.screen.get_width() - self.sprite_w) // 2
            y = 250
            self.game.screen.blit(self.current_controls_frame, (x, y))

        instructions_page.add.vertical_margin(50)
        instructions_page.set_onupdate(advance_frame)
        instructions_page.mainloop(self.game.screen)
