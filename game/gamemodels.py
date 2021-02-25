'''
WWII Pacific Front - gamemodels.py
(C) 2021 Jesus Trujillo, Delaney Siggia, Calvin Guela, Anthony Jaimes, Rocco Carrozza
---
This module is responsible for multiplayer capabilities.
'''

import sys
from pathlib import Path
import pygame

class Ship(pygame.sprite.Sprite):
    def __init__(self, width, height, pos_x, pos_y, color): #varibles ship has

        super().__init__()
        self.image = pygame.Surface([width, height])
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.center = [pos_x,pos_y]

class Grid(pygame.sprite.Sprite):
    def __init__(self, width, height, pos_x, pos_y, color): #varibles grid has

        super().__init__()
        self.image = pygame.Surface([width, height])
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.center = [pos_x,pos_y]

class Background(pygame.sprite.Sprite):
    def __init__(self, image_file, location):
        pygame.sprite.Sprite.__init__(self)  #call Sprite initializer
        self.image = pygame.image.load(Path(__file__).parent / 'assets' / 'ship (3).png')
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = location

#General setup
pygame.init()
clock = pygame.time.Clock()

#Game Screen
screen_width = 1000
screen_height = 600
screen = pygame.display.set_mode((screen_width,screen_height))
background = Background('../assets/ocean.png', [0,0])

#Grid
g1 = Grid(10,500,100,300,(255,255,255))
g2 = Grid(10,500,200,300,(255,255,255))
g3 = Grid(10,500,300,300,(255,255,255))
g4 = Grid(10,500,400,300,(255,255,255))
g5 = Grid(10,500,500,300,(255,255,255))
g6 = Grid(10,500,600,300,(255,255,255))
g7 = Grid(10,500,700,300,(255,255,255))
g8 = Grid(10,500,800,300,(255,255,255))
g9 = Grid(10,500,900,300,(255,255,255))

v1 = Grid(900,10,500,125,(100,0,200))
v2 = Grid(900,10,200,300,(255,255,255))
v3 = Grid(900,10,300,300,(255,255,255))
v4 = Grid(10,500,400,300,(255,255,255))
v5 = Grid(10,500,500,300,(255,255,255))
v6 = Grid(10,500,600,300,(255,255,255))
v7 = Grid(10,500,700,300,(255,255,255))
v8 = Grid(10,500,800,300,(255,255,255))
v9 = Grid(10,500,900,300,(255,255,255))

grid_group = pygame.sprite.Group()
grid_group.add(g1,g2,g3,g4,g5,g6,g7,g8,g9,v1,v2,v3,v4,v5,v6,v7,v8,v9)

#Ships
#ship = Ship(100,25,400,300,(255,255,255))
#ship_group = pygame.sprite.Group()
#ship_group.add(ship)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    
    pygame.display.flip()
    screen.fill([255, 255, 255])
    screen.blit(background.image, background.rect)

    grid_group.draw(screen)
    clock.tick(60)

#if __name__ == '__main__':
    # Write test code here...
    #pygame.init()
