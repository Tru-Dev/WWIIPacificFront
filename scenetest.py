import pygame
import pygame.freetype
from game import gamemodels

pygame.init()


gamemodels.GameLoop('menu_main', (800, 600)).run()
