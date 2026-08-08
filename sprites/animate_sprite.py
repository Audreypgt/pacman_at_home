import pygame, sys, os
pygame.init()

DISPLAY_W, DISPLAY_H = 800, 600
canvas = pygame.Surface((DISPLAY_W, DISPLAY_H))
window = pygame.display.set_mode((DISPLAY_W, DISPLAY_H))

class Sprite(pygame.sprite.Sprite):

    CELL = 47
    SPRITE_W = 40
    SPRITE_H = 40

    def __init__(self, filename):
        self.sheet = pygame.image.load(filename).convert_alpha()

    def get_sprite(self, x, y, w, h):
        sprite = pygame.Surface((w, h), pygame.SRCALPHA)
        sprite.blit(self.sheet, (0, 0), (x, y, w, h))
        return sprite

    def get_sprite_at(self, row, col, w=None, h=None):
        w = w or self.SPRITE_W
        h = h or self.SPRITE_H
        return self.get_sprite(col * self.CELL, row * self.CELL, w, h)

class Pacwoman:
    def __init__(self, x, y, sprite_sheet):
        self.x = x
        self.y = y
        self.direction = (1, 0)
        self.move_speed = 3
        self.animation_speed = 6
        self.move_timer = 0
        self.frame_index = 0
        self.state = "idle"


my_sheet = Sprite('sprites/pac_sheet.png')

pacwoman_frames = [my_sheet.get_sprite_at(row, 17) for row in range(9)]

ROTATION = {"right": 0, "up": 90, "left": 180, "down": 270}

SPEED = 3
ANIMATION_SPEED = 6

pacwoman_x, pacwoman_y = DISPLAY_W // 2, DISPLAY_H // 2
facing = "right"
frame_index = 0
frame_timer = 0
clock = pygame.time.Clock()

run = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    keys = pygame.key.get_pressed()
    moving = False

    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        pacwoman_x -= SPEED
        facing = "left"
        moving = True
    elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        pacwoman_x += SPEED
        facing = "right"
        moving = True
    elif keys[pygame.K_UP] or keys[pygame.K_w]:
        pacwoman_y -= SPEED
        facing = "up"
        moving = True
    elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
        pacwoman_y += SPEED
        facing = "down"
        moving = True

    pacwoman_x = max(0, min(DISPLAY_W - Sprite.SPRITE_W, pacwoman_x))
    pacwoman_y = max(0, min(DISPLAY_H - Sprite.SPRITE_H, pacwoman_y))

    if moving:
        frame_timer += 1
        if frame_timer >= ANIMATION_SPEED:
            frame_timer = 0
            frame_index = (frame_index + 1) % len(pacwoman_frames)

    canvas.fill((0, 0, 0))
    current_frame = pygame.transform.rotate(pacwoman_frames[frame_index], ROTATION[facing])
    canvas.blit(current_frame, (pacwoman_x, pacwoman_y))
    window.blit(canvas, (0, 0))
    pygame.display.update()
    clock.tick(60)

pygame.quit()