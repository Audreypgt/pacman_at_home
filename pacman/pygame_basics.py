import pygame
from pygame.locals import *


class App:
    def __init__(self):
        self._running = True
        self._display_surf = None
        self.size = self.weight, self.height = 640, 400

    def on_init(self):
        """
        calls pygame.init() that initialize all pygame modules then creates a display
        and trys to use hardware acceleration and ends by setting running to true
        """
        pygame.init()
        self._display_surf = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        self._running = True

    def on_event(self, event):
        """
        checks if quit event happened if so sets _running 
        to false to break the game loop
        """
        if event.type == pygame.QUIT:
            self._running = False

    def on_loop(self):
        pass

    def on_render(self):
        pass

    def on_cleanup(self):
        """calls pygame.quit() that quits all pygame modules"""
        pygame.quit()

    def on_execute(self):
        """
        initialize pygame than enter main loop in which check events 
        and then computes and render everything until _running is true and
        only quit event will set it to false
        """
        if self.on_init() == False:
            self._running = False

        while self._running:
            for event in pygame.event.get():
                self.on_event(event)
            self.on_loop()
            self.on_render()
        self.on_cleanup()


if __name__ == "__main__":
    theApp = App()
    theApp.on_execute()