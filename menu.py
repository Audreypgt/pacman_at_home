import pygame_menu  # type: ignore
from pygame_menu import themes
from pac_man import GameController


class Gamemenus:

    def __init__(self, game: GameController):
        self.game = game

    def start_menu(self) -> None:
        main_menu = pygame_menu.Menu(
            "PacWoman", 600, 400, theme=themes.THEME_SOLARIZED)
        main_menu.add.button("Play", self.game.set_up_game)
        main_menu.add.button("Instructions", self.instructions_menu)
        main_menu.add.button("Quit", pygame_menu.events.EXIT)
        main_menu.mainloop(self.game.screen)

    def pause_menu(self) -> None:
        main_menu = pygame_menu.Menu(
            "PacWOman", 600, 400, theme=themes.THEME_SOLARIZED)
        main_menu.add.button("Resume", self.game.start_game)
        main_menu.add.button("Restart", self.game.restart_game)
        main_menu.add.button("Quit", pygame_menu.events.EXIT)
        main_menu.mainloop(self.game.screen)

    def over_menu(self) -> None:
        self.game.over = True
        title = "You Win!" if self.game.won else "Game Over"

        main_menu = pygame_menu.Menu(
            title, 600, 500, theme=themes.THEME_SOLARIZED)
        main_menu.add.label(f"Score: {self.game.pacgums.score}")
        self.game.player = main_menu.add.text_input("Name: ", default="Player")
        main_menu.add.button("Save & View Leaderboard", self.leaderboard_menu)
        if self.game.won and self.game.current_level < self.game.max_level:
            main_menu.add.button("Next Level", self.game.next_level)
        main_menu.add.button("Restart", self.game.restart_game)
        main_menu.add.button(
            "Quit", self.game.quit_game_over)
        main_menu.mainloop(self.game.screen)

    def leaderboard_menu(self) -> None:
        self.game.save_score(self.game.player.get_value())

        board_menu = pygame_menu.Menu(
            "Top 10 Scores", 600, 500, theme=themes.THEME_SOLARIZED)
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
            "Instructions", 600, 800, theme=themes.THEME_SOLARIZED)

        instructions_page.add.label("How to Play")
        instructions_page.add.label("Move with the arrow keys")
        instructions_page.add.label("Eat all pacgums to win")
        instructions_page.add.label("Avoid the ghosts!")
        instructions_page.add.label("Super PacGums let you eat ghosts")
        instructions_page.add.vertical_margin(20)
        instructions_page.add.button("Back", self.start_menu)
        instructions_page.mainloop(self.game.screen)
