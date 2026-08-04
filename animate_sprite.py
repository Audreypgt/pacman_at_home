import pygame
from pygame.locals import *
import sys

pygame.init()

screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Spritesheet Animation")

def load_frames(sheet, x, y, frame_width, frame_height, num_frames):
    frames = []

    for i in range(num_frames):
        frame = sheet.subsurface(
            pygame.Rect(x + i * frame_width, y, frame_width, frame_height)
        )
        frames.append(frame)

    return frames

