
from parsing import parse
from game_controller import GameController


if __name__ == "__main__":
    # try:
        configuration = parse()
        game = GameController(configuration)
        game.set_background()

        # start from starting menu
        game.menus.start_menu()
    # except Exception as e:
    #     print(e)
