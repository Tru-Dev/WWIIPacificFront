import sys
from pathlib import Path
import pygame

# Background for code

class Background(pygame.sprite.Sprite):
    def __init__(self, image_file, location):
        pygame.sprite.Sprite.__init__(self) 
        self.image = pygame.image.load(Path(__file__).parent.parent / 'assets' / image_file) # line of code to call file
        self.image = pygame.transform.scale(self.image, (screen_width,screen_height)) #changes background to screen size
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = location

# Pointer for code

class Crosshair(pygame.sprite.Sprite):
    def __init__(self, image_file, location):
        super().__init__()
        self.image = pygame.image.load(Path(__file__).parent.parent / 'assets' / image_file) # line of code to call file
        self.rect = self.image.get_rect()
    def update(self): # Makes crosshair follow mouse inputs
        self.rect.center = pygame.mouse.get_pos()

# Ships in code

class Ship(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y,image_file,location): 

        super().__init__()
        self.image = pygame.image.load(Path(__file__).parent.parent / 'assets' / image_file) # line of code to call file
        self.rect = self.image.get_rect()
        self.rect.center = [pos_x,pos_y]

# Grid for code

class Grid(pygame.sprite.Sprite):
    def __init__(self, width, height, pos_x, pos_y, color):

        super().__init__()
        self.image = pygame.Surface([width, height])
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.center = [pos_x,pos_y]

if __name__ == '__main__':

    #General setup
    pygame.init()
    clock = pygame.time.Clock()

    #Game Screen
    screen_width = 1280
    screen_height = 700
    screen = pygame.display.set_mode((screen_width,screen_height), pygame.RESIZABLE)
    background = Background('ocean.png', [0, 0])

    #Grid
    v1 = Grid(8, 600, 600, 350, (0,0,0))
    v2 = Grid(8, 600, 300, 350, (0,0,0))
    v3 = Grid(8, 600, 200, 350, (0,0,0))
    v4 = Grid(8, 600, 500, 350, (0,0,0))
    v5 = Grid(8, 600, 400, 350, (0,0,0))
    v6 = Grid(8, 600, 700, 350, (0,0,0))
    v7 = Grid(8, 600, 100, 350, (0,0,0))

    h1 = Grid(600, 8, 402, 250, (0,0,0))
    h2 = Grid(600, 8, 402, 450, (0,0,0))
    h3 = Grid(600, 8, 402, 350, (0,0,0))
    h4 = Grid(600, 8, 402, 150, (0,0,0))
    h5 = Grid(600, 8, 402, 550, (0,0,0))
    h6 = Grid(600, 8, 402, 650, (0,0,0))
    h7 = Grid(600, 8, 402, 750, (0,0,0))
    h8 = Grid(600, 8, 402, 50, (0,0,0))

    grid_group = pygame.sprite.Group()
    grid_group.add(v1,v2,v3,v4,v5,v6,v7,h1,h2,h3,h4,h5,h6,h7,h8)

# Where game is ran 

while True:
    
    pygame.display.flip()
    screen.fill([100, 160, 255]) #Gives a blue background
    screen.blit(background.image, background.rect)
    #pygame.draw.rect(screen, (0,0,0), pygame.Rect(screen.get_width() - 5 - (screen.get_width() / 5), 50, screen.get_width() / 5,50))
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT: # Closes code when game is exited out
            pygame.quit()
            sys.exit()
        if event.type == pygame.VIDEORESIZE: # Allows user to resize the game screen
            screen = pygame.display.set_mode((event.w,event.h), pygame.RESIZABLE)
            

    grid_group.draw(screen) #Adds the grid screen 
    #hip_group.draw(screen) #Adds the ships
    #crosshair_group.draw(screen) #Adds the pointer
    #crosshair_group.update() #Updates the pointer to mouse outputs
    
    pygame.display.update()
    clock.tick(60)