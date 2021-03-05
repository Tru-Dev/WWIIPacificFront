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

pygame.init()

mainClock = pygame.time.Clock()
pygame.display.set_caption('game base')
screen = pygame.display.set_mode((800,600),0,32)

font = pygame.freetype.Font(Path(__file__).parent.parent / 'assets' / 'font' / 'CutiveMono-Regular.ttf', 40)
font2 = pygame.freetype.Font(Path(__file__).parent.parent / 'assets' / 'font' / 'CutiveMono-Regular.ttf', 20)

background = Background('menubg.png', [0,0])

def draw_text(text,font,color,surface,x,y):
    textobj, textrect = font.render(text,color)
    textrect.topleft = (x,y)
    surface.blit(textobj, textrect)

def game():
    running = True
    while running:
        screen.fill((0,0,0))
        draw_text('Game',font, (255,255,255), screen,350,50)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        pygame.display.update()
        mainClock.tick(60)  

def multiplayer():
    running = True
    while running:
        screen.fill((0,0,0))
        draw_text('Multiplayer',font, (255,255,255), screen,350,50)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        pygame.display.update()
        mainClock.tick(60)  

def main_menu():
    while True:

        pygame.display.flip()
        screen.blit(background.image, background.rect)
        #screen.fill((0,0,0))
        draw_text('Main Menu',font, (0,0,0), screen,300,50)

        mx, my = pygame.mouse.get_pos()

        button_1 = pygame.Rect(50,100,200,50)
        button_2 = pygame.Rect(50,200,200,50)
        button_3 = pygame.Rect(550,100,200,50)
        button_4 = pygame.Rect(550,200,200,50)

        if button_1.collidepoint((mx,my)):
            if click:
                story()
            
        if button_2.collidepoint((mx,my)):
            if click:
                multiplayer()

        if button_3.collidepoint((mx,my)):
            if click:
                free_play() 

        if button_4.collidepoint((mx,my)):
            if click:
                options() 

        

        pygame.draw.rect(screen, (255,255,255), button_1)
        pygame.draw.rect(screen, (255,255,255), button_2)
        pygame.draw.rect(screen, (255,255,255), button_3)
        pygame.draw.rect(screen, (255,255,255), button_4)

        draw_text('Start Story',font2, (0,0,0), screen,78,120)
        draw_text('Multiplayer',font2, (0,0,0), screen,78,220)
        draw_text('Free Play',font2, (0,0,0), screen,590,120)
        draw_text('Options',font2, (0,0,0), screen,600,220)

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

def story():
    running = True
    while running:
        screen.fill((0,0,0))
        draw_text('Story',font, (255,255,255), screen,350,50)
        
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

def multiplayer():
    running = True
    while running:
        screen.fill((0,0,0))
        draw_text('Multiplayer',font, (255,255,255), screen,300,50)
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

def free_play():
    running = True
    while running:
        screen.fill((0,0,0))
        draw_text('Free Play',font, (255,255,255), screen,300,50)
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
        draw_text('Options',font, (255,255,255), screen,300,50)
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