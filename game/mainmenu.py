from pathlib import Path
import sys

import pygame
import pygame.freetype
import pygame.display
import pygame.image
import pygame.transform


class Background(pygame.sprite.DirtySprite):
    def __init__(self, image_file,location):
        super().__init__()  #call Sprite initializer
        self.image = pygame.image.load(Path(__file__).parent.parent / 'assets' / 'img' / image_file)
        self.image = pygame.transform.scale(self.image, (800, 600))
        self.rect = self.image.get_rect()

mainClock = pygame.time.Clock()
from pygame.locals import *
pygame.init()
pygame.display.set_caption('game base')
screen = pygame.display.set_mode((800,600),0,32)

font = pygame.freetype.Font(Path(__file__).parent.parent / 'assets' / 'font' / 'CutiveMono-Regular.ttf', 40)

background = Background('mback.jpg', [0,0])

def draw_text(text,font,color,surface,x,y):
    textobj = font.render(text,1,color)
    textrect = textobj.get_rect()
    textrect.topleft = (x,y)
    surface.blit(textobj, textrect)

def main_menu():
    while True:

        pygame.display.flip()
        screen.blit(background.image, background.rect)
        #screen.fill((0,0,0))
        draw_text('Main Menu',font, (0,0,0), screen,300,50)

        mx, my = pygame.mouse.get_pos()

        button_1 = pygame.Rect(50,100,200,50)
        button_2 = pygame.Rect(50,200,200,50)

        if button_1.collidepoint((mx,my)):
            if click:
                game()
            
        if button_2.collidepoint((mx,my)):
            if click:
                options()

        pygame.draw.rect(screen, (255,255,255), button_1)
        pygame.draw.rect(screen, (255,0,0), button_2)

        click = False

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        pygame.quit()
                        sys.exit()
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True
        pygame.display.update()
        mainClock.tick(60)

def game():
    running = True
    while running:
        screen.fill((0,0,0))
        draw_text('Game',font, (255,255,255), screen,350,50)
        
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        running = False

        pygame.display.update()
        mainClock.tick(60)  

def options():
    running = True
    while running:
        screen.fill((0,0,0))
        draw_text('Options',font, (255,255,255), screen,350,50)
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        running = False
        pygame.display.update()
        mainClock.tick(60)  

main_menu()