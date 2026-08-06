import pygame, sys, os
# pygame.init()

# window_size = (800, 600)
# game_window = pygame.display.set_mode(window_size)

class Sprite(pygame.sprite.Sprite):

    CELL = 47
    SPRITE_W = 40
    SPRITE_H = 40

    def __init__(self, image):
        self.image = image
        self.sheet = self.image.load(image).convert_alpha()

    def get_sprite(self, x, y, w, h):
        sprite = pygame.Surface((w, h), pygame.SRCALPHA)
        sprite.blit(self.sheet, (0, 0), (x, y, w, h))
        return sprite

    def get_sprite_at(self, row, col, w=None, h=None):
        w = w or self.SPRITE_W
        h = h or self.SPRITE_H
        x = col * self.CELL
        y = row * self.CELL
        return self.get_sprite(x, y, w, h)


# my_sprite = 

# run = True
# while run:
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             run = False

#     keys = pygame.key.get_pressed()
#     if keys[pygame.K_LEFT] or keys[pygame.K_a]:
#         right1.rect.x -= 5
#     if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
#         right1.rect.x += 5
#     if keys[pygame.K_UP] or keys[pygame.K_w]:
#         right1.rect.y -= 5
#     if keys[pygame.K_DOWN] or keys[pygame.K_s]:
#         right1.rect.y += 5

#     game_window.fill((0, 0, 0))
#     sprites.draw(game_window)
#     pygame.display.update()

# pygame.quit()