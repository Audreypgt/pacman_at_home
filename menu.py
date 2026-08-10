import pygame

def main_menu():
    #for all the menu background, titles, button
    pass

def game_loop(self) -> None:
    """create maze, check user inputs and render new elements"""
    self.clock = pygame.time.Clock()
    self.time = 0.0
    print(self.clock)
    while self.running:
        # menu.main_menu._open(loading)
        self.screen.fill("black")
        self.update()
        self.time += self.clock.tick(60) / 1000
        self.time = round(self.time, 2)
        print(self.time)
        self.render(self.mazegen)
        # game ends after 90 seconds and goes back to menu
        if self.time == 90.00:
            self.running = False
    self.running = True

def pause_menu():
    pass

def game_over_screen():
    #final score, name input, restart/quit
    pass

def set_difficulty(self, difficulty) -> None:
    """select difficulty level from menu"""
    pass

# def select_level(main_menu):
#     main_menu._open(level)
# call check events ? to check which choice the user makes
# for ex we have 10 buttons, so in check events, if button #10
# is pressed, then call function for level 10

while True:
    if current_scene == "main_menu":
        main_menu()
    elif current_scene == "game":
        game_loop()
    elif current_scene == "pause":
        pause_menu()
    elif current_scene == "game_over":
        game_over_screen()


class MainMenu:
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.K_ENTER:
                return "game"
        return "main_menu"

    def update(self):
        pass

    def draw(self, screen):
        screen.fill((0,0,0))
        draw_text("MAIN MENU", 100)
        draw_text("Press ENTER to Start", 200)