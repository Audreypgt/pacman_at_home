import pygame
from pygame.locals import *
import sys

pygame.init()

screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Spritesheet Animation")
spritesheet = pygame.image.load("sprites/pac_sheet.png").convert_alpha()

def load_frames(sheet, x, y, frame_width, frame_height, num_frames):
    frames = []

    for i in range(num_frames):
        frame = sheet.subsurface(
            pygame.Rect(x + i * frame_width, y, frame_width, frame_height)
        )
        frames.append(frame)

    return frames

frames = load_frames(spritesheet, 790, 1, 43, 43, 12)
current_frame = 0
animation_speed = 0.10
clock = pygame.time.Clock()
carryOn = True
while carryOn:
    screen.fill((30, 30, 30))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    current_frame += animation_speed
    if current_frame >= len(frames):
        current_frame = 0

    screen.blit(frames[int(current_frame)], (100, 300))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
