import pygame
# pygame.init()

# DISPLAY_W, DISPLAY_H = 800, 600
# canvas = pygame.Surface((DISPLAY_W, DISPLAY_H))
# window = pygame.display.set_mode((DISPLAY_W, DISPLAY_H))

class PacSpriteSheet():

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
    def __init__(self, x, y, sprite_sheet, screen_w, screen_y):
        self.x = x
        self.y = y
        self.screen_w = screen_w
        self.screen_y = screen_y
        self.direction = (1, 0)
        self.move_speed = 3
        self.animation_speed = 3.5
        self.move_timer = 0
        self.frame_index = 0
        self.state = "idle"
        self.frame_sets = {
            (-1, 0): [sprite_sheet.get_sprite_at(8, 17) ,sprite_sheet.get_sprite_at(7, 17), sprite_sheet.get_sprite_at(6, 17)],
            (1, 0): [sprite_sheet.get_sprite_at(0, 17) ,sprite_sheet.get_sprite_at(1, 17), sprite_sheet.get_sprite_at(2, 17)],
            (0, 1): [sprite_sheet.get_sprite_at(3, 17), sprite_sheet.get_sprite_at(4, 17), sprite_sheet.get_sprite_at(5, 17)],
            (0, -1): [sprite_sheet.get_sprite_at(9, 17), sprite_sheet.get_sprite_at(10,17), sprite_sheet.get_sprite_at(11, 17)]
        }
        self.current_frame = self.frame_sets[self.direction][0]

    def input(self, keys):
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.direction = (-1, 0)
            self.state = "moving"
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.direction = (1, 0)
            self.state = "moving"
        elif keys[pygame.K_UP] or keys[pygame.K_w]:
            self.direction = (0, -1)
            self.state = "moving"
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.direction = (0, 1)
            self.state = "moving"

    def move(self):
        if self.state == "moving":
            new_x = self.x + self.direction[0] * self.move_speed
            new_y = self.y + self.direction[1] * self.move_speed
            clamped_x = max(0, min(self.screen_w- PacSpriteSheet.SPRITE_W, new_x))
            clamped_y = max(0, min(self.screen_y - PacSpriteSheet.SPRITE_H, new_y))

            if clamped_x == self.x and clamped_y == self.y:
                self.state = "idle"
            else:
                self.x, self.y = clamped_x, clamped_y


    def update(self):
        
        if self.state == "moving":
            self.move_timer += 1
            if self.move_timer >= self.animation_speed:
                self.move_timer = 0
                self.frame_index = (self.frame_index + 1) % 3
            self.current_frame = self.frame_sets[self.direction][self.frame_index]

    def draw(self, surface):
        surface.blit(self.current_frame, (self.x, self.y))

# sprite_sheet = PacSpriteSheet("sprites/pac_sheet.png")
# pacwoman = Pacwoman(DISPLAY_W // 2, DISPLAY_H // 2, sprite_sheet)
# clock = pygame.time.Clock()

# run = True
# while run:
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             run = False

#     keys = pygame.key.get_pressed()
#     pacwoman.input(keys)
#     pacwoman.move()
#     pacwoman.update()

#     canvas.fill((0, 0, 0))
#     pacwoman.draw(canvas)
#     window.blit(canvas, (0, 0))
#     pygame.display.update()
#     clock.tick(60)

# pygame.quit()