import pygame 

from consts import *

class FallingToken(object):

    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color

    def render(self, surface):
        pygame.draw.circle(
            surface,
            C_LIST[self.color],
            (self.x + TOKEN_CONTENT_SIZE / 2, self.y + TOKEN_CONTENT_SIZE / 2),
            TOKEN_R
        )
