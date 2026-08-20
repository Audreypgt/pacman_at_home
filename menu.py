import pygame_menu  # type: ignore
from pygame_menu import themes
from pac_man import GameController


class Gamemenus:

    def __init__(self, game: GameController):
        self.game = game

    def start_menu(self) -> None:
        main_menu = pygame_menu.Menu(
            "PacWOman", 600, 400, theme=themes.THEME_SOLARIZED)
        main_menu.add.button("Play", self.game.set_up_game)
        # main_menu.add.button("Select level", select_level(main_menu))
        main_menu.add.button("Select level")
        # main_menu.add.button("Select difficulty??", game.set_difficulty)
        # select difficulty could send you to a menu page with only the
        # difficulty and a button like <hard> and when you press -> key it
        # changes the difficulty, then you press enter and you go back to
        # the main menu
        main_menu.add.button("Quit", pygame_menu.events.EXIT)
        main_menu.mainloop(self.game.screen)

    def pause_menu(self) -> None:
        main_menu = pygame_menu.Menu(
            "PacWOman", 600, 400, theme=themes.THEME_SOLARIZED)
        main_menu.add.button("Restart", self.game.set_up_game)
        main_menu.add.button("Resume", self.game.start_game)
        main_menu.add.button("Quit", pygame_menu.events.EXIT)
        main_menu.mainloop(self.game.screen)

    def over_menu(self) -> None:
        self.game.over = True
        title = "You Win !" if self.game.won else "Game Over"

        main_menu = pygame_menu.Menu(
            title, 600, 500, theme=themes.THEME_SOLARIZED)

        main_menu.add.label(f"Score: {self.game.pacgums.score}")
        self.game.looser = main_menu.add.text_input("Name: ", default="Player")
        main_menu.add.button("Save & View Leaderboard", self.leaderboard_menu)
        main_menu.add.button("Restart", self.game.set_up_game)
        main_menu.add.button(
            "Quit", self.game.quit_game_over)
        # ERROR ================= pygame.error: video system not initialized
        main_menu.mainloop(self.game.screen)

    def leaderboard_menu(self) -> None:
        self.game.save_score(self.game.looser.get_value())

        board_menu = pygame_menu.Menu("Top 10 Scored", 600, 500, 
                                      theme=themes.THEME_SOLARIZED)
        top_scores = self.game.get_top_scores()
        if not top_scores:
            board_menu.add.label("No scores yet")
        for i, (name, score) in enumerate(top_scores, start=1):
            board_menu.add.label(f"{i}. {name}: {score}")
        board_menu.add.button("Restart", self.game.set_up_game)
        board_menu.add.button("Quit", pygame_menu.events.EXIT)
        board_menu.mainloop(self.game.screen)

    # def set_difficulty(self, difficulty) -> None:
    #     """select difficulty level from menu"""
    #     pass

    # def select_level(main_menu):
    #     main_menu._open(level)
    # call check events ? to check which choice the user makes
    # for ex we have 10 buttons, so in check events, if button #10
    # is pressed, then call function for level 10
