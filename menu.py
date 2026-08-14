import pygame_menu
from pygame_menu import themes


class Gamemenus:
    def __init__(self, game):
        self.game = game

    def start_menu(self):
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

    def pause_menu(self):
        main_menu = pygame_menu.Menu(
            "PacWOman", 600, 400, theme=themes.THEME_SOLARIZED)
        main_menu.add.button("Restart", self.game.set_up_game)
        main_menu.add.button("Resume", self.game.start_game)
        main_menu.add.button("Quit", pygame_menu.events.EXIT)
        main_menu.mainloop(self.game.screen)

    def over_menu(self):
        self.game.over = True
        main_menu = pygame_menu.Menu(
            "PacWOman", 600, 400, theme=themes.THEME_SOLARIZED)
        self.game.looser = main_menu.add.text_input("Name: ", default="LOOSER")
        main_menu.add.button("Restart", self.game.set_up_game)
        main_menu.add.button(
            "Give up like you did with your dreams", self.game.quit_game_over)
        # ERROR ================= pygame.error: video system not initialized
        main_menu.mainloop(self.game.screen)

    # def set_difficulty(self, difficulty) -> None:
    #     """select difficulty level from menu"""
    #     pass

    # def select_level(main_menu):
    #     main_menu._open(level)
    # call check events ? to check which choice the user makes
    # for ex we have 10 buttons, so in check events, if button #10
    # is pressed, then call function for level 10
