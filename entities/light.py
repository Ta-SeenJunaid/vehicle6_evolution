# entities/light.py
import pygame

class Light:
    def __init__(self, x, y, radius=15):
        self.x = x
        self.y = y
        self.radius = radius

    def move(self, new_position):
        self.x, self.y = new_position

    @property
    def pos(self):
        return (self.x, self.y)

    def draw(self, surface):
        pygame.draw.circle(surface, (255, 220, 0), (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, (0, 0, 0), (int(self.x), int(self.y)), self.radius, 2)