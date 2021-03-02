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
    def __init__(self, pos_x, pos_y,image_file,location): #varibles ship has

        super().__init__()
        self.image = pygame.image.load(Path(__file__).parent.parent / 'assets' / 'img' / image_file)
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
        self.image = pygame.image.load(Path(__file__).parent.parent / 'assets' / 'img' / image_file)
        self.image = pygame.transform.scale(self.image, (800, 600))
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = location

class Crosshair(pygame.sprite.Sprite):
    def __init__(self, image_file, location):
        super().__init__()
        self.image = pygame.image.load(Path(__file__).parent.parent / 'assets' / 'img' / image_file)
        self.rect = self.image.get_rect()
    def update(self):
        self.rect.center = pygame.mouse.get_pos()

if __name__ == '__main__':

    #General setup
    pygame.init()
    clock = pygame.time.Clock()

    #Game Screen
    screen_width = 800
    screen_height = 600
    screen = pygame.display.set_mode((screen_width,screen_height))
    background = Background('ocean.png', [0, 0])
    #bg = pygame.transform.scale(background, (800,600))
    
    #Grid
    v1 = Grid(10, 420, 400, 310, (100,200,100))
    v2 = Grid(10, 420, 300, 310, (100,200,100))
    v3 = Grid(10, 420, 200, 310, (100,200,100))
    v4 = Grid(10, 420, 500, 310, (100,200,100))
    v5 = Grid(10, 420, 600, 310, (100,200,100))

    h1 = Grid(628, 10, 402, 200, (100,200,100))
    h2 = Grid(628, 10, 402, 400, (100,200,100))
    h3 = Grid(628, 10, 402, 300, (100,200,100))
    h4 = Grid(628, 10, 402, 200, (100,200,100))
    h1 = Grid(628, 10, 402, 500, (100,200,100))
    grid_group = pygame.sprite.Group()
    grid_group.add(v1,v2,v3,v4,v5,h1,h2,h3,h4)
    
    #Ships
    s1 = Ship(150,250,'ship (3).png', [0,0])
    s2 = Ship(350,150,'ship (3).png', [0,0])
    s3 = Ship(450,350,'ship (3).png', [0,0])
    s4 = Ship(660,450,'ship (3).png', [0,0])
    ship_group = pygame.sprite.Group()
    ship_group.add(s1,s2,s3,s4)

    #Crosshair
    crosshair = Crosshair('crosshair.png', [0,0])
    crosshair_group = pygame.sprite.Group()
    crosshair_group.add(crosshair)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        pygame.display.flip()
        screen.fill([100, 160, 255])
        screen.blit(background.image, background.rect)

        grid_group.draw(screen)
        ship_group.draw(screen)
        crosshair_group.draw(screen)
        crosshair_group.update()
        
        clock.tick(60)


        #
        # Write test code here...
        #pygame.init()
