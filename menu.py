import os
import pygame  # type: ignore
import pygame_menu  # type: ignore
from pygame_menu import themes
from pac_man import GameController
import pac_man
from pacwoman import PacSpriteSheet

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
        self.started_menu = True
        self.theme = pacwoman_theme()
        self.pacwoman_logo = pygame.image.load(
            "sprites/pacwoman_logo.png")
        self.x = (self.game.screen.get_width()) // 5
        self.y = 50
        self.font = pygame.font.SysFont(self.theme.title_font, 50)
        start_text = self.font.render(
            "Press SPACE to start", True, pac_man.YELLOW)
        instruc_text = self.font.render(
            "Press H for instructions", True, pac_man.YELLOW)
        ldbd_text = self.font.render(
            "Press L for leaderboard", True, pac_man.YELLOW)
        # mainmen_text used in pause menu and leaderboard, but either can come
        # before the other so i put it here
        self.mainmen_text = self.font.render(
            "Press M to go back to main menu", True, pac_man.YELLOW)
        self.quit_text = self.font.render(
            "Press Q to quit", True, pac_man.YELLOW)

        while self.started_menu:
            self.game.screen.fill(pac_man.BLACK)
            self.game.screen.blit(self.pacwoman_logo, (self.x, self.y))
            self.game.screen.blit(start_text, (self.x, self.y + 300))
            self.game.screen.blit(instruc_text, (self.x, self.y + 400))
            self.game.screen.blit(ldbd_text, (self.x, self.y + 500))
            self.game.screen.blit(self.quit_text, (self.x, self.y + 600))

            self.game.check_events()
            pygame.display.update()

        self.game.set_up_game()

    def pause_menu(self) -> None:
        self.paused_menu = True
        resume_text = self.font.render(
            "Press SPACE to resume", True, pac_man.YELLOW)
        restart_text = self.font.render(
            "Press ENTER to restart", True, pac_man.YELLOW)

        while self.paused_menu:

            self.game.screen.fill(pac_man.BLACK)
            self.game.screen.blit(self.pacwoman_logo, (self.x, self.y))
            self.game.screen.blit(resume_text, (self.x, self.y + 300))
            self.game.screen.blit(restart_text, (self.x, self.y + 400))
            self.game.screen.blit(self.mainmen_text, (self.x, self.y + 500))
            self.game.screen.blit(self.quit_text, (self.x, self.y + 600))

            self.game.check_events()
            pygame.display.update()

    # TO DO ---------------------------------------------------------------
    def over_menu(self) -> None:
        self.game.over = True
        title = "You Win!" if self.game.won else "Game Over"

        main_menu = pygame_menu.Menu(
            title, 600, 500, theme=pacwoman_theme(600, 500))
        main_menu.add.label(f"Score: {self.game.pacgums.score}")
        self.game.player = main_menu.add.text_input(
            "Name: ", default="Player")
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
        self.ldbd_menu = True
        self.title_font = pygame.font.SysFont(self.theme.title_font, 75)
        self.scores_font = pygame.font.SysFont(self.theme.title_font, 30)
        title = self.title_font.render("Top 10 Scores", True, pac_man.PINK)
        no_scores = self.font.render(
            "No scores yet", True, pac_man.WHITE)
        self.nxt_lv_txt = self.font.render(
            "Press N for next level", True, pac_man.YELLOW)

        if save_current:
            self.game.save_score(self.game.player.get_value())
        top_scores = self.game.get_top_scores()

        while self.ldbd_menu:
            self.game.screen.fill(pac_man.BLACK)
            self.game.screen.blit(self.pacwoman_logo, (self.x, self.y))
            self.game.screen.blit(title, (self.x + 50, self.y + 220))

            if not top_scores:
                self.game.screen.blit(no_scores, (self.x, self.y + 320))
            else:
                add_y = 320
                for i, (name, score) in enumerate(top_scores, start=1):
                    score = self.scores_font.render(
                        f"{i}. {name}: {score}", True, pac_man.WHITE)
                    self.game.screen.blit(score, (self.x, self.y + add_y))
                    add_y += 40
                    if i == 5:
                        break
                add_y = 320
                add_x = 300
                for i, (name, score) in enumerate(top_scores, start=1):
                    if i > 5:
                        score = self.scores_font.render(
                            f"{i}. {name}: {score}", True, pac_man.WHITE)
                        self.game.screen.blit(score, (
                            self.x + add_x, self.y + add_y))
                        add_y += 40

                if self.game.won and (self.game.current_level
                                      < self.game.max_level):
                    add_y += 20
                    self.game.screen.blit(self.nxt_lv_txt, (
                        self.x, self.y + add_y))
                    add_y += 50
                    self.game.screen.blit(self.mainmen_text, (
                        self.x, self.y + add_y))
                    add_y += 50
                    self.game.screen.blit(self.quit_text, (
                        self.x, self.y + add_y))
                else:
                    add_y += 50
                    self.game.screen.blit(self.mainmen_text, (
                        self.x - 50, self.y + add_y))

            self.game.check_events()
            pygame.display.update()

    # TO DO ---------------------------------------------------------------
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
