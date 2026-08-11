import pygame


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

class GameScene:
    def handle_events(self, events):
        pass

    def update(self):
        pass

    def draw(self, screen):
        pass


class GameOver:
    def handle_events(self, events):
        pass

    def update(self):
        pass

    def draw(self, screen):
        pass


class PauseScene:
    def handle_events(self, events):
        pass

    def update(self):
        pass

    def draw(self, screen):
        pass

def main_menu():
    #for all the menu background, titles, button
    pass

def game_loop(self) -> None:
    """create maze, check user inputs and render new elements"""
    self.clock = pygame.time.Clock()
    self.time = 0.0
    print(self.clock)
    while self.running:
        self.screen.fill("black")
        self.update()
        self.time += self.clock.tick(60) / 1000
        self.time = round(self.time, 2)
        print(self.time)
        self.render(self.mazegen)
        if self.time == 90.00:
            self.running = False
    self.running = True

def pause_menu():
    pass

def game_over_screen():
    #final score, name input, restart/quit
    pass

# def set_difficulty(self, difficulty) -> None:
#     """select difficulty level from menu"""
#     pass

# def select_level(main_menu):
#     main_menu._open(level)
# call check events ? to check which choice the user makes
# for ex we have 10 buttons, so in check events, if button #10
# is pressed, then call function for level 10

scenes = {
    "main_menu": MainMenu(),
    "game": GameScene(),
    "game_over": GameOver()
}

current_scene = "main_menu"

while True:
    events = pygame.event.get()
    if any(event.type == pygame.QUIT for event in events):
        pygame.quit()
        sys.exit()

    next_scene = scenes[current_scene].handle_events(events)
    current_scene = next_scene

    scenes[current_scene].update()
    scenes[current_scene].draw(screen)

    pygame.display.flip()
    clock.tick(60)