import pygame
import sys
import os

font = pygame.font.Font(None, 36)

score_text = font.render(f'Score: {score}', True, (255, 255, 255))
screen.blit(score_text, (1, 1))
font = pygame.font.Font('arial.ttf', 48)