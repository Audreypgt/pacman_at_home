import pygame  # type: ignore
from pygame_menu import widgets  # type: ignore
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
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)

WALL_WIDTH = 12
WALL_INNER_WIDTH = 4


class GameController(object):
    def __init__(self) -> None:
        # prevent circular import in menu.py:
        from menu import Gamemenus

        self.level_seeds = {
            1: configuration.levels["level_1"].seed,
            2: configuration.levels["level_2"].seed,
            3: configuration.levels["level_3"].seed,
            4: configuration.levels["level_4"].seed,
            5: configuration.levels["level_5"].seed,
            6: configuration.levels["level_6"].seed,
            7: configuration.levels["level_7"].seed,
            8: configuration.levels["level_8"].seed,
            9: configuration.levels["level_9"].seed,
            10: configuration.levels["level_10"].seed,
            }

        pygame.init()
        self.screen = pygame.display.set_mode(SCREENSIZE, 0, 32)
        self.game_surface = self.screen.subsurface(
            pygame.Rect(0, GUI_HEIGHT, GAME_WIDTH, GAME_HEIGHT))
        self.background: pygame.surface.Surface = None
        self.maze_surface: pygame.surface.Surface = None
        self.running = False
        self.scatter = False
        self.over = False
        self.won = False
        self.player: widgets.TextInput = None
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
        self.pacwoman.move(mazegen)
        self.pacwoman.update()
        self.pacgums.eat(self.pacwoman, configuration)
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
                    mazegen, spawn[0], spawn[1])
            else:
                self.ghost_move: dict[str, Callable[..., Any]] = {
                    "blinky": partial(
                        self.blinky.bfs_move, mazegen, self.pacwoman),
                    "inky": partial(
                        self.inky.inky_move, mazegen, self.pacwoman),
                    "pinky": partial(
                        self.pinky.bfs_move, mazegen, self.pacwoman),
                    "clyde": partial(
                        self.clyde.clyde_move, mazegen, self.pacwoman,
                        spawn[0], spawn[1]),
                    "scatter": partial(
                        ghost.scatter_move, mazegen, spawn[0],
                        spawn[1]),
                    "scared": partial(
                        ghost.move_random, mazegen),
                    }
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

    def get_wall_segments(self, mazegen: MazeGenerator) -> list[tuple[
            tuple[int, int], tuple[int, int]]]:
        """collect every wall edge of the maze as line segments"""
        segments: list[tuple[tuple[int, int], tuple[int, int]]] = []
        cy = 0
        for line in mazegen.maze:
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

    def build_maze_surface(self, mazegen: MazeGenerator) -> None:
        surface = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
        segments = self.get_wall_segments(mazegen)

        # thick pink skeleton
        for seg in segments:
            self.draw_capsule(surface, PINK, seg, WALL_WIDTH)

        # black inner layer, thinner, to hollow out the wall
        for seg in segments:
            self.draw_capsule(surface, BLACK, seg, WALL_INNER_WIDTH)

        self.maze_surface = surface

    def draw_maze(self, mazegen: MazeGenerator) -> None:
        if self.maze_surface is None:
            self.build_maze_surface(mazegen)
        self.game_surface.blit(self.maze_surface, (0, 0))

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
            with open(configuration.highscore_filename, 'a') as f:
                f.write(
                    f"{self.player.get_value()}: {self.pacgums.score}\n")
            self.sort_score_file()
            self.over = False
        self.clock = pygame.time.Clock()
        self.time = configuration.lvl_max_time
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
            self.lives = configuration.lives
        saved_score = self.pacgums.score
        mazegen.generate(self.level_seeds[self.current_level])
        # to reset the walls between each levels, so that in level 2 you dont
        # get level 1 walls, its cache.
        self.maze_surface = None

        # Pacwoman
        maze_width = len(mazegen.maze[0])
        maze_height = len(mazegen.maze)
        center_col: int = maze_width // 2
        center_row: int = maze_height // 2
        spawn_x: int = center_col * 50 + (50 - self.sprite_w) // 2
        spawn_y: int = center_row * 50 + (50 - self.sprite_h) // 2
        self.pacwoman_spawn = (spawn_x, spawn_y)
        self.pacwoman = Pacwoman(
            spawn_x, spawn_y, pac_sheet, GAME_WIDTH, GAME_HEIGHT)

        self.pacgums.init_gums(
            mazegen, self.pacwoman, self.current_level, configuration)
        if not reset_progress:
            self.pacgums.score = saved_score

        # Blinky
        spawn_x_blky = (
            len(mazegen.maze[0]) - 1) * 50 + (
                50 - self.sprite_w) // 2
        spawn_y_blky = (
            len(mazegen.maze) - 1) * 50 + (
                50 - self.sprite_h) // 2
        self.blinky_spawn = (spawn_x_blky, spawn_y_blky)
        self.blinky = Blinky(
            spawn_x_blky, spawn_y_blky, pac_sheet,
            GAME_WIDTH, GAME_HEIGHT)

        # Pinky
        spawn_x_pky = (50 - self.sprite_w) // 2
        spawn_y_pky = (
            len(mazegen.maze) - 1) * 50 + (
                50 - self.sprite_h) // 2
        self.pinky_spawn = (spawn_x_pky, spawn_y_pky)
        self.pinky = Pinky(
            spawn_x_pky, spawn_y_pky, pac_sheet, GAME_WIDTH, GAME_HEIGHT)

        # Clyde
        self.clyde_spawn = (0, 0)
        self.clyde = Clyde(
            0, 0, pac_sheet, GAME_WIDTH, GAME_HEIGHT)

        # Inky
        spawn_x_inky = (len(mazegen.maze[0]) - 1) * 50 + (
                50 - self.sprite_w) // 2
        spawn_y_inky = (50 - self.sprite_h) // 2
        self.inky_spawn = (spawn_x_inky, spawn_y_inky)
        self.inky = Inky(
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
            self.render(mazegen)

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
                    self.pacgums.score += configuration.points_per_ghost
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

        # with open(configuration.highscore_filename, 'r') as f:
            # scores: str = f.read()
            # if name in scores:
            #     score_1 = self.dict_scores[name]
            #     score_2 = self.pacgums.score
            #     if score_1 > score_2:
            #         return

        try:
            self.dict_scores[name]
            score_1 = self.dict_scores[name]
            score_2 = self.pacgums.score
            if score_1 > score_2:
                return
        except KeyError:
            with open(configuration.highscore_filename, 'a') as f:
                f.write(f"{name}: {self.pacgums.score}\n")
            self.dict_scores.update({name: self.pacgums.score})
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
        if self.won and self.current_level == self.max_level:
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


if __name__ == "__main__":
    # try:
    configuration = parse()
    game = GameController()
    game.set_background()
    mazegen = MazeGenerator()

    # start from starting menu
    game.menus.start_menu()
    # except Exception as e:
    #     print(e)
