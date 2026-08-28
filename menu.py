import os
import pygame  # type: ignore
import pygame_menu  # type: ignore
from pygame_menu import themes
from pac_man import GameController
from pacwoman import PacSpriteSheet

SPRITES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sprites")


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


class Gamemenus:

    def __init__(self, game: GameController):
        self.game = game
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
            full.subsurface((i * self.sprite_w, 0, self.sprite_w, self.sprite_h))
            for i in range(self.num_frames)
        ]
        self.controls_frame_index = 0
        self.controls_animation_speed = 1.5
        self.controls_timer = 0
        self.current_controls_frame = self.controls_frames[0]

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
            "PacWoman", 600, 400, theme=pacwoman_theme(600, 400))
        main_menu.add.button("Play", self.game.set_up_game)
        main_menu.add.button("Instructions", self.instructions_menu)
        main_menu.add.button("Leaderboard", self.leaderboard_menu)
        main_menu.add.button("Quit", pygame_menu.events.EXIT)
        main_menu.mainloop(self.game.screen)

    def pause_menu(self) -> None:
        main_menu = pygame_menu.Menu(
            "PacWoman", 600, 400, theme=pacwoman_theme(600, 400))
        main_menu.add.button("Resume", self.game.start_game)
        main_menu.add.button("Restart", self.game.restart_game)
        main_menu.add.button("Main Menu", self.start_menu)
        main_menu.add.button("Quit", pygame_menu.events.EXIT)
        main_menu.mainloop(self.game.screen)

    def over_menu(self) -> None:
        self.game.over = True
        title = "You Win!" if self.game.won else "Game Over"

        main_menu = pygame_menu.Menu(
            title, 600, 500, theme=pacwoman_theme(600, 500))
        main_menu.add.label(f"Score: {self.game.pacgums.score}")
        self.game.player = main_menu.add.text_input("Name: ", default="Player")
        main_menu.add.button(
            "Save & View Leaderboard",
            lambda: self.leaderboard_menu(save_current=True),
        )
        if self.game.won and self.game.current_level < self.game.max_level:
            main_menu.add.button("Next Level", self.game.next_level)
        main_menu.add.button("Restart", self.game.restart_game)
        main_menu.add.button(
            "Quit", self.game.quit_game_over)
        main_menu.mainloop(self.game.screen)

    def leaderboard_menu(self, save_current: bool = False) -> None:
        if save_current:
            self.game.save_score(self.game.player.get_value())

        board_menu = pygame_menu.Menu(
            "Top 10 Scores", 600, 500, theme=pacwoman_theme(600, 500))
        top_scores = self.game.get_top_scores()
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
            "Instructions", 600, 800, theme=pacwoman_theme(600, 800))

        instructions_page.add.label("How to Play")
        instructions_page.add.vertical_margin(self.sprite_h + 20)
        instructions_page.add.label("Move with the arrow keys")
        instructions_page.add.label("Eat all pacgums to win")
        instructions_page.add.label("Avoid the ghosts!")
        instructions_page.add.label("Super PacGums let you eat ghosts")
        instructions_page.add.vertical_margin(20)
        instructions_page.add.button("Back", self.start_menu)

        def advance_frame() -> None:
            self.update()
            x = (self.game.screen.get_width() - self.sprite_w) // 2
            y = 250
            self.game.screen.blit(self.current_controls_frame, (x, y))

        instructions_page.set_onupdate(advance_frame)
        instructions_page.mainloop(self.game.screen)
