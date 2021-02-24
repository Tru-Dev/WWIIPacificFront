'''
WWII Pacific Front - gamemodels.py
(C) 2021 Jesus Trujillo, Delaney Siggia, Calvin Guela, Anthony Jaimes, Rocco Carrozza
---
This module is responsible for multiplayer capabilities.
'''

import pygame

#creating ship object
class Ship(pygame.sprite.Sprite):
    def __init__(self, color, length, width, model): #varibles ship has

        pygame.sprite.Sprite(self)

        self.image = pygame.Surface([width, width])
        self.image.fill(color)

        self.rect = self.image.get_rect()

if __name__ == '__main__':
    # Write test code here...
    pygame.init()

