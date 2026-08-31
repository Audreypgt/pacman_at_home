import pygame  # type: ignore
from pacwoman import PacSpriteSheet
from mazegenerator import MazeGenerator  # type: ignore
from pacwoman import Pacwoman

MAZE_CELL = 50


class Pacgums:
    def __init__(self, sprite_sheet: PacSpriteSheet, gum_row: int,
                 gum_col: int, sp_gum_row: int, sp_gum_col: int,
                 scared_duration: float = 10.0) -> None:
        self.gums: set[tuple[int, int]] = set()
        self.score: int = 0
        self.eat_ghosts: bool = False
        self.scared_duration: float = scared_duration
        self.scared_timer: float = 0.0
        self.sprite_h = 42
        self.sprite_w = 42

        self.pacgum_img = pygame.transform.scale(
            sprite_sheet.get_sprite_at(gum_row, gum_col), (25, 25))
        self.sp_pacgum_img = pygame.transform.scale(
            sprite_sheet.get_sprite_at(sp_gum_row, sp_gum_col), (40, 40))

    def init_gums(self, mazegen: MazeGenerator, pacwoman: Pacwoman,
                  current_level, configuration) -> None:
        # some variables en double, normal ?
        self.gums = set()
        self.super_gum = set()
        self.eat_ghosts = False
        self.scared_timer = 0.0

        pac_col = (pacwoman.x + self.sprite_w // 2) // MAZE_CELL
        pac_row = (pacwoman.y + self.sprite_h // 2) // MAZE_CELL

        i = 0
        level_pacgums = configuration.levels[f"level_{current_level}"].pacgum
        for row, lines in enumerate(mazegen.maze):
            for col, cell in enumerate(lines):
                if i >= level_pacgums:
                    break
                elif cell != 15:
                    self.gums.add((row, col))
                    i += 1

        self.gums.discard((pac_row, pac_col))

        maze_height = len(mazegen.maze)
        maze_width = len(mazegen.maze[0])
        corners = [
            (0, 0),
            (0, maze_width - 1),
            (maze_height - 1, 0),
            (maze_height - 1, maze_width - 1)
        ]

        for row, col in corners:
            self.gums.discard((row, col))
            self.super_gum.add((row, col))

        self.score = 0

    def eat(self, pacwoman: Pacwoman, configuration: dict) -> None:
        center_x = pacwoman.x + self.sprite_w // 2
        center_y = pacwoman.y + self.sprite_h // 2
        col = center_x // MAZE_CELL
        row = center_y // MAZE_CELL

        if (row, col) in self.gums:
            self.gums.discard((row, col))
            self.score += configuration.points_per_pacgum
        elif (row, col) in self.super_gum:
            self.super_gum.discard((row, col))
            self.score += configuration.points_per_super_pacgum
            self.eat_ghosts = True
            self.scared_timer = self.scared_duration

    def update(self, dt: float) -> None:
        if self.eat_ghosts:
            self.scared_timer -= dt
        if self.scared_timer <= 0:
            self.eat_ghosts = False
            self.scared_timer = 0.0

    def draw(self, screen: pygame.surface.Surface) -> None:
        gum_size = self.pacgum_img.get_width()
        gum_offset = (MAZE_CELL - gum_size) / 2
        for row, col in self.gums:
            cx = col * MAZE_CELL
            cy = row * MAZE_CELL
            screen.blit(self.pacgum_img, (cx + gum_offset, cy + gum_offset))

        blink_on = (pygame.time.get_ticks() // 250) % 2 == 0
        if blink_on:
            sp_size = self.sp_pacgum_img.get_width()
            sp_offset = (MAZE_CELL - sp_size) / 2
            for row, col in self.super_gum:
                cx = col * MAZE_CELL
                cy = row * MAZE_CELL
                screen.blit(self.sp_pacgum_img,
                            (cx + sp_offset, cy + sp_offset))
