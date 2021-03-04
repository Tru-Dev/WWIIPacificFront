# WWII: Pacific Front - gamemodels.py
# (C) 2021 Jesus Trujillo, Delaney Siggia, Calvin Guela, Anthony Jaimes, Rocco Carrozza

'''
This module defines the game classes.
'''

from pathlib import Path
from typing import Final, List, Tuple, Union, overload
from math import copysign
from enum import IntFlag, auto

import numpy as np
import pygame
import pygame.sprite
import pygame.image
import pygame.display
import pygame.mouse
import pygame.draw
import pygame.transform
import pygame.time
import pygame.event
import pygame.key
import pygame.surfarray

TILE_SIZE: Final[int] = 64

class OceanBGSegment(pygame.sprite.DirtySprite):
    def __init__(self, menubg: 'MenuBackground', layer: int):
        super().__init__(menubg)

class MenuBackground(pygame.sprite.LayeredDirty):
    def __init__(self, screen_size: Tuple[int, int]) -> None:
        super().__init__()
        self.bg_base = pygame.image.load(
            Path(__file__).parent.parent / 'assets' / 'img' / 'oceanbg.png'
        )
        

class Player:
    def __init__(self) -> None:
        pass

class USPlayer(Player):
    pass

class JapanPlayer(Player):
    '''
    Multiplayer-only Japan player
    '''
    pass

class JapanCPUPlayer(Player):
    '''
    Regular Japan player
    '''
    pass

class SingleTileOverlay(pygame.sprite.DirtySprite):
    def __init__(
        self,
        color: pygame.Color,
        pos: Tuple[int, int],
        *groups: pygame.sprite.AbstractGroup,
        layer: int=800,
        offset: Tuple[int, int]=(0, 0)
    ) -> None:
        self._layer = layer
        super().__init__(*groups)
        self.color = color
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image.set_colorkey(~color)
        tx, ty = pos
        ox, oy = offset
        self.rect = self.image.fill(~color).move(tx * TILE_SIZE, ty * TILE_SIZE)
        self.rect.move_ip(ox % TILE_SIZE, oy % TILE_SIZE)
        
        pygame.draw.rect(self.image, color, self.image.get_rect(), 2, 16)


class FiredTile(pygame.sprite.DirtySprite):
    def __init__(
        self,
        hit: bool,
        pos: Tuple[int, int],
        *groups: pygame.sprite.AbstractGroup,
        layer: int=20,
        offset: Tuple[int, int]=(0, 0)
    ) -> None:
        self._layer = layer
        super().__init__(*groups)
        self.hit = hit
        img_file = 'hit.png' if hit else 'miss.png'
        self.image = pygame.image.load(
            Path(__file__).parent.parent / 'assets' / 'img' / img_file
        ).convert()
        self.image.set_colorkey(pygame.Color('Magenta'))
        tx, ty = pos
        ox, oy = offset
        self.rect = self.image.get_rect().move(tx * TILE_SIZE, ty * TILE_SIZE)
        self.rect.move_ip(ox % TILE_SIZE, oy % TILE_SIZE)

        self.dirty = 2

        bordercolor = pygame.Color('Red' if hit else 'White')
        pygame.draw.rect(self.image, bordercolor, self.image.get_rect(), 2, 16)

    def update(self, *args, **kwargs) -> None:
        mod_ticks = pygame.time.get_ticks() % 2000
        if mod_ticks // 1000 == 0:
            self.image.set_alpha(255 - mod_ticks // 8)
        else:
            self.image.set_alpha(5 + mod_ticks // 8)

class Ship(pygame.sprite.DirtySprite):
    def __init__(
        self,
        pos: Tuple[int, int],
        img_file: str,
        *groups: pygame.sprite.AbstractGroup,
        layer: int=10
    ):
        self._layer = layer
        self.image = pygame.image.load(Path(__file__).parent.parent / 'assets' / 'img' / img_file)
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.rect.x *= TILE_SIZE
        self.rect.y *= TILE_SIZE
        self.tile_rect = pygame.Rect(pos, (self.rect.w // TILE_SIZE, self.rect.h // TILE_SIZE))
        super().__init__(*groups)

class ShipGroup(pygame.sprite.Group):
    def __init__(self, *sprites: Ship) -> None:
        self.ship_tiles = {}
        super().__init__(*sprites)
    
    def add_internal(self, sprite: Ship) -> None:
        super().add_internal(sprite)
        self.ship_tiles.update({
            (x, y): sprite
                for x in range(sprite.tile_rect.left, sprite.tile_rect.right)
                for y in range(sprite.tile_rect.top, sprite.tile_rect.bottom)
        })

class ShotStyle(IntFlag):
    CLASSIC = auto()
    CLEAN = auto()
    BOTH = CLASSIC | CLEAN

class FiringGrid(pygame.sprite.DirtySprite):
    def __init__(
        self,
        size: Tuple[int, int],
        style: ShotStyle,
        ship_group: ShipGroup,
        *groups: pygame.sprite.AbstractGroup,
        layer: int=800,
        offset: Tuple[int, int]=(0, 0)
    ) -> None:
        self._layer = layer
        super().__init__(*groups)
        w, h = size
        ox, oy = offset
        self.rect = pygame.Rect(ox, oy, w * TILE_SIZE, h * TILE_SIZE)
        ckey = pygame.Color('Magenta')
        self.image = pygame.Surface(self.rect.size)
        self.image.fill(ckey)
        self.image.set_colorkey(ckey)
        self.hit_img = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.hit_img.fill(ckey)
        self.hit_img.set_colorkey(ckey)
        self.miss_img = self.hit_img.copy()
        if style & ShotStyle.CLASSIC:
            self.hit_img.blit(pygame.image.load(
                Path(__file__).parent.parent / 'assets' / 'img' / 'hit.png'
            ), (0, 0))
            self.miss_img.blit(pygame.image.load(
                Path(__file__).parent.parent / 'assets' / 'img' / 'miss.png'
            ), (0, 0))
        if style & ShotStyle.CLEAN:
            pygame.draw.rect(
                self.hit_img, pygame.Color('Red'), self.hit_img.get_rect(), 2, 16
            )
            pygame.draw.rect(
                self.miss_img, pygame.Color('White'), self.miss_img.get_rect(), 2, 16
            )
        self.style = style
        self.ship_group = ship_group
        self.shots = [[False for i in range(w)] for j in range(h)]
        self.dirty = 2

    def shoot(self, pos: Tuple[int, int]) -> bool:
        x, y = pos
        self.shots[y][x] = True
        if pos in self.ship_group.ship_tiles:
            self.image.blit(self.hit_img, (x * TILE_SIZE, y * TILE_SIZE))
            return True
        else:
            self.image.blit(self.miss_img, (x * TILE_SIZE, y * TILE_SIZE))
            return False

    def update(self, *args, **kwargs) -> None:
        mod_ticks = pygame.time.get_ticks() % 2000
        if mod_ticks // 1000 == 0:
            self.image.set_alpha(255 - mod_ticks // 8)
        else:
            self.image.set_alpha(5 + mod_ticks // 8)


class Grid(pygame.sprite.DirtySprite):
    def __init__(self, width, height, pos_x, pos_y, color): #varibles grid has
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.center = [pos_x,pos_y]

class OverlayGrid(pygame.sprite.DirtySprite):
    def __init__(
        self,
        pos: Tuple[int, int],
        size: Tuple[int, int],
        *groups: pygame.sprite.AbstractGroup,
        color: pygame.Color=pygame.Color(127, 200, 255),
        layer: int=750
    ) -> None:
        self._layer = layer
        super().__init__(*groups)
        w, h = size
        sw, sh = w * TILE_SIZE, h * TILE_SIZE
        px, py = pos
        self.image = pygame.Surface((sw, sh))
        rect_img = pygame.Surface((TILE_SIZE, TILE_SIZE))
        ckey = ~color # Guaranteed to be different
        self.image.set_colorkey(ckey)
        rect_img.fill(ckey)
        pygame.draw.rect(rect_img, color, rect_img.get_rect(), 2, 16)
        for i in range(w):
            for j in range(h):
                self.image.blit(rect_img, ((px + i) * TILE_SIZE, (py + j) * TILE_SIZE))
        self.rect = self.image.get_rect().move(px * TILE_SIZE, py * TILE_SIZE)


class Background(pygame.sprite.DirtySprite):
    def __init__(self, image_file):
        super().__init__()  #call Sprite initializer
        self.image = pygame.image.load(Path(__file__).parent.parent / 'assets' / 'img' / image_file)
        self.image = pygame.transform.scale(self.image, (800, 600))
        self.rect = self.image.get_rect()

class TiledBackground(pygame.sprite.DirtySprite):
    def __init__(
        self,
        img_file: str,
        size: Tuple[int, int],
        *groups: pygame.sprite.AbstractGroup,
        layer: int=-1000
    ) -> None:
        self._layer = layer
        super().__init__(*groups)
        w, h = size
        self.image = pygame.Surface((w * TILE_SIZE, h * TILE_SIZE))
        bgtile_img = pygame.image.load(
            Path(__file__).parent.parent / 'assets' / 'img' / img_file
        ).convert()
        bgtile_rect = bgtile_img.get_rect()
        pygame.draw.line(
            bgtile_img,
            pygame.Color(127, 200, 255),
            (bgtile_rect.w - 1, 0),
            (bgtile_rect.w - 1, bgtile_rect.h)
        )
        pygame.draw.line(
            bgtile_img,
            pygame.Color(127, 200, 255),
            (0, bgtile_rect.h - 1),
            (bgtile_rect.w, bgtile_rect.h - 1)
        )

        self.rect = self.image.get_rect()

        img_w, img_h = bgtile_img.get_rect().size
        for i in range(w):
            for j in range(h):
                self.image.blit(bgtile_img, (i * img_w, j * img_h))

class Crosshair(pygame.sprite.DirtySprite):
    def __init__(self, img_file: str, *groups: pygame.sprite.AbstractGroup) -> None:
        self._layer = 1000 # set to a large amount so it is in front of everything
        super().__init__(*groups)
        self.image = pygame.image.load(Path(__file__).parent.parent / 'assets' / 'img' / img_file)
        self.rect = self.image.get_rect()

    def update(self):
        self.rect.center = pygame.mouse.get_pos()

class InvertCrosshair:
    def __init__(self, mask_file: str, img_file: str) -> None:
        mask = pygame.image.load(Path(__file__).parent.parent / 'assets' / 'img' / mask_file)
        self.image = pygame.image.load(Path(__file__).parent.parent / 'assets' / 'img' / img_file)
        self.image.set_colorkey(pygame.Color('White'))
        self.rect = self.image.get_rect()
        self.truth_arr = np.array(pygame.surfarray.pixels2d(mask) & 0xFFFFFF, dtype=bool)
        self.dirty = 1
        
    def draw(self, surf: pygame.Surface) -> List[pygame.Rect]:
        if self.dirty == 0:
            return []
        elif self.dirty == 1:
            self.dirty = 0
        self.rect.center = pygame.mouse.get_pos()
        self.rect.clamp_ip(surf.get_rect())
        surfarr = pygame.surfarray.pixels3d(surf.subsurface(self.rect))

        intermediate_array: np.ndarray = np.array(
            np.average(surfarr[self.truth_arr], 1) // 128, dtype=np.int8
        ).reshape((-1, 1)) * 255

        surfarr[self.truth_arr] = np.concatenate((intermediate_array, ) * 3, axis=1)
        del surfarr

        surf.blit(self.image, self.rect)
        return [self.rect]

class SnapCrosshair(pygame.sprite.DirtySprite):
    def __init__(self, color: pygame.Color, *groups: pygame.sprite.AbstractGroup) -> None:
        self._layer = 1000
        super().__init__(*groups)
        self.color = color
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image.set_colorkey(~color)
        self.rect = self.image.fill(~color)
        pygame.draw.rect(self.image, color, self.rect.move(-32, -32), 4, 16)
        pygame.draw.rect(self.image, color, self.rect.move(32, -32), 4, 16)
        pygame.draw.rect(self.image, color, self.rect.move(-32, 32), 4, 16)
        pygame.draw.rect(self.image, color, self.rect.move(32, 32), 4, 16)
        pygame.draw.rect(self.image, color, self.rect, 4, 16)
    
    def update(self, *args, offset: Tuple[int, int], **kwargs) -> None:
        mx, my = pygame.mouse.get_pos()
        ox, oy = offset
        self.rect.x = mx - (mx - ox) % TILE_SIZE
        self.rect.y = my - (my - oy) % TILE_SIZE

class ScrollingGroup(pygame.sprite.LayeredDirty):
    def __init__(
        self,
        ref_spr: pygame.sprite.DirtySprite,
        *sprites: pygame.sprite.DirtySprite,
        base_velocity: int=3,
        **kwargs
    ) -> None:
        super().__init__(ref_spr, *sprites, **kwargs)
        self.ref_spr = ref_spr
        self.base_velocity = base_velocity
        self.velx = 0
        self.vely = 0
        self.keys_dirty = False
        self.vel_dirty = False
    
    def update(self, *args, **kwargs) -> None:
        super().update(*args, **kwargs)
        ref_rect = pygame.Rect(self.ref_spr.rect)
        sw, sh = pygame.display.get_window_size()

        if self.keys_dirty:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_w] or keys[pygame.K_UP]:
                self.vely = self.base_velocity
            if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                self.vely = -self.base_velocity
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                self.velx = -self.base_velocity
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                self.velx = self.base_velocity
            if all(
                map(lambda k: not keys[k], [pygame.K_w, pygame.K_UP, pygame.K_s, pygame.K_DOWN])
            ):
                self.vely = 0
            if all(
                map(lambda k: not keys[k], [pygame.K_a, pygame.K_LEFT, pygame.K_d, pygame.K_RIGHT])
            ):
                self.velx = 0
            self.keys_dirty = False

        if self.vel_dirty:
            if self.velx != 0:
                self.velx = int(copysign(self.base_velocity, self.velx))
            if self.vely != 0:
                self.vely = int(copysign(self.base_velocity, self.vely))
            self.vel_dirty = False

        effective_velx = self.velx
        effective_vely = self.vely

        if ref_rect.left >= -1:
            ref_rect.left = 0
            effective_velx = min(0, effective_velx)
        if ref_rect.top >= -1:
            ref_rect.top = 0
            effective_vely = min(0, effective_vely)
        if ref_rect.right <= sw + 1:
            ref_rect.right = sw
            effective_velx = max(0, effective_velx)
        if ref_rect.bottom <= sh + 1:
            ref_rect.bottom = sh
            effective_vely = max(0, effective_vely)

        if (effective_velx, effective_vely) == (0, 0):
            return

        for spr in self:
            if spr.dirty == 0:
                spr.dirty = 1
            spr.rect.move_ip(effective_velx, effective_vely)

    def get_offset(self) -> Tuple[int, int]:
        return self.ref_spr.rect.topleft

if __name__ == '__main__':

    #General setup
    pygame.init()
    clock = pygame.time.Clock()

    #Game Screen
    screen_width = 800
    screen_height = 600
    screen = pygame.display.set_mode((screen_width,screen_height), flags=pygame.RESIZABLE)
    background = TiledBackground('ocean.png', (30, 30))
    #bg = pygame.transform.scale(background, (800,600))

    base_vel = 3
    shift_vel = 5

    board_group = ScrollingGroup(background, base_velocity=base_vel)
    overlay_grid = OverlayGrid((0, 0), (30, 30), board_group)
    overlay_grid.visible = 0

    ui_group = pygame.sprite.LayeredDirty()

    #Ships

    ship_group = ShipGroup()
    s1 = Ship((0, 0), 'essex.png', board_group, ship_group)
    s2 = Ship((5, 1), 'essex.png', board_group, ship_group)
    s3 = Ship((10, 0), 'essex.png', board_group, ship_group)
    s4 = Ship((15, 1), 'essex.png', board_group, ship_group)
    s5 = Ship((20, 0), 'essex.png', board_group, ship_group)

    firegrid = FiringGrid((30, 30), ShotStyle.CLASSIC, ship_group, board_group)
    print(firegrid.shoot((0, 0)))
    print(firegrid.shoot((1, 1)))

    #Crosshair
    crosshair = SnapCrosshair(pygame.Color('Black'), ui_group)

    # pygame.mouse.set_visible(False) # hide the mouse for the crosshair

    running = True

    render_group = pygame.sprite.LayeredDirty(*board_group, *ui_group)

    MOVEMENT_KEYS: Final[List[int]] = [
        pygame.K_w, pygame.K_UP,
        pygame.K_a, pygame.K_LEFT,
        pygame.K_s, pygame.K_DOWN,
        pygame.K_d, pygame.K_RIGHT,
    ]

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key in (pygame.K_LSHIFT, pygame.K_RSHIFT):
                    overlay_grid.visible = 1
                    crosshair.dirty = 1
                    board_group.base_velocity = shift_vel
                    board_group.vel_dirty = True
                    board_group.keys_dirty = True
                if event.key in MOVEMENT_KEYS:
                    board_group.keys_dirty = True
            if event.type == pygame.KEYUP:
                if event.key in (pygame.K_LSHIFT, pygame.K_RSHIFT):
                    overlay_grid.visible = 0
                    crosshair.dirty = 1
                    board_group.base_velocity = base_vel
                    board_group.vel_dirty = True
                    board_group.keys_dirty = True
                if event.key in MOVEMENT_KEYS:
                    board_group.keys_dirty = True
            if event.type == pygame.MOUSEMOTION:
                crosshair.dirty = 1
                background.dirty = 1
            if event.type == pygame.VIDEORESIZE:
                background.dirty = 1


        board_group.update()

        ui_group.update(offset=board_group.get_offset())

        pygame.display.update(render_group.draw(screen) + ui_group.draw(screen))

        
        pygame.display.set_caption(f'gamemodels test (fps: {clock.get_fps()})')

        clock.tick(60)
