# WWII: Pacific Front - gamemodels.py
# (C) 2021 Jesus Trujillo, Delaney Siggia, Calvin Guela, Anthony Jaimes, Rocco Carrozza

'''
This module defines the game classes.
'''

from pathlib import Path
from typing import Callable, Final, List, Tuple
from math import copysign
from enum import IntFlag, auto
import re

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
import pygame.freetype

TILE_SIZE: Final[int] = 64

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
    def __init__(
        self,
        img_file: str,
        size: Tuple[int, int],
        *groups: pygame.sprite.AbstractGroup,
        layer: int=-1000
    ):
        self._layer = layer
        super().__init__(*groups)
        self.base_image = pygame.image.load(
            Path(__file__).parent.parent / 'assets' / 'img' / img_file
        )
        self.image = pygame.transform.scale(self.base_image, size)
        self.rect = self.image.get_rect()

    def resize(self, size: Tuple[int, int]) -> None:
        self.image = pygame.transform.scale(self.base_image, size)
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

class Button(pygame.sprite.DirtySprite):
    def __init__(
        self,
        rect: pygame.Rect,
        text: str,
        font: pygame.freetype.Font,
        fg: pygame.Color,
        bg: pygame.Color,
        click: Callable,
        *groups: pygame.sprite.AbstractGroup,
        text_size: int=24,
        layer: int=20,
        border_radius: int=20,
        ckey: pygame.Color=pygame.Color('Magenta')
    ) -> None:
        self._layer = layer
        super().__init__(*groups)
        self.rect = rect
        self.text = text
        self.fg = fg
        self.bg = bg
        self.font = font
        self.text_size = text_size
        self.image = pygame.Surface(rect.size)
        self.ckey = ckey
        self.border_radius = border_radius
        self.image.fill(ckey)
        self.image.set_colorkey(ckey)
        pygame.draw.rect(self.image, bg, self.image.get_rect(), border_radius=border_radius)
        text_rect = self.font.get_rect(text, size=text_size)
        text_rect.center = self.image.get_rect().center
        self.font.render_to(self.image, text_rect, None, fg, size=text_size)
        self.base_image = self.image.copy()
        self.hover_image = self.image.copy()
        self.hover_image.fill(pygame.Color('#404040'), special_flags=pygame.BLEND_SUB)
        self.hover_image.set_colorkey(pygame.Color('#BF00BF'))
        self.hover = False
        self.click = click
        self.clicked = False

    def update(self, *args, **kwargs) -> None:
        mpos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mpos):
            if not self.hover:
                self.hover = True
                self.image = self.hover_image
                self.dirty = 1
            mdown = pygame.mouse.get_pressed()[0]
            if mdown and self.hover and not self.clicked:
                self.click()
                self.clicked = True
            elif self.clicked:
                self.clicked = False
        elif self.hover:
            self.hover = False
            self.image = self.base_image
            self.dirty = 1

class TextInput(pygame.sprite.DirtySprite):
    def __init__(
        self,
        rect: pygame.Rect,
        font: pygame.freetype.Font,
        fg: pygame.Color,
        bg: pygame.Color,
        *groups: pygame.sprite.AbstractGroup,
        default_text: str='',
        text_size: int=24,
        layer: int=20,
        focus: bool=False
    ) -> None:
        self._layer = layer
        super().__init__(*groups)
        pygame.key.set_repeat(500, 25)
        self.rect = rect
        self.text = default_text
        self.cursor = len(self.text)
        self.fg = fg
        self.bg = bg
        self.font = font
        self.text_size = text_size
        self.image = pygame.Surface(rect.size)
        self.image.fill(bg)
        text_rect = self.font.get_rect(self.text, size=text_size).move(text_size // 2, 0)
        text_rect.centery += self.image.get_rect().centery
        self.font.render_to(self.image, text_rect, None, fg, size=text_size)
        self.focus = focus
        self.curs_rect = pygame.Rect(0, 0, 3, font.get_sized_height(text_size))
        self.curs_rect.centery = self.image.get_rect().centery
        self.curs_vis = False

    def update(self, *args, **kwargs) -> None:
        mpos = pygame.mouse.get_pos()
        mdown = pygame.mouse.get_pressed()[0]
        if self.rect.collidepoint(mpos) and mdown:
            self.focus = True
        elif mdown:
            self.focus = False
        self.image.fill(self.bg)
        text_rect = self.font.get_rect(self.text, size=self.text_size).move(self.text_size // 2, 0)
        text_rect.centery = self.image.get_rect().centery
        self.font.render_to(self.image, text_rect, None, self.fg, size=self.text_size)
        tick_comp = pygame.time.get_ticks() % 2000 >= 1000
        if tick_comp and not self.curs_vis and self.focus:
            self.curs_vis = True
            self.dirty = 1
        elif not tick_comp and self.curs_vis:
            self.curs_vis = False
            self.dirty = 1
        if self.curs_vis:
            curs_offset = self.font.get_rect(self.text[:self.cursor], size=self.text_size).right
            self.image.fill(self.fg, self.curs_rect.move(curs_offset + self.text_size // 2, 0))
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        if not self.focus:
            return False
        if event.type == pygame.TEXTINPUT:
            self.text = (
                self.text[:self.cursor] + event.text + self.text[self.cursor:]
            )
            self.cursor += 1
            self.dirty = 1
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                return True
            elif event.key == pygame.K_BACKSPACE:
                if len(self.text[:self.cursor]) > 0:
                    if event.mod & (pygame.KMOD_CTRL | pygame.KMOD_ALT):
                        text_until_cursor = self.text[:self.cursor]
                        idx_from_end = re.search(r'(?!^)(\b)', text_until_cursor[::-1]).start()
                        self.text = (
                            text_until_cursor[:-idx_from_end] + self.text[self.cursor:]
                        )
                        self.cursor -= idx_from_end
                    else:
                        self.text = (
                            self.text[:self.cursor - 1] + self.text[self.cursor:]
                        )
                        self.cursor -= 1
                    self.dirty = 1
            elif event.key == pygame.K_DELETE:
                if self.cursor < len(self.text):
                    if event.mod & (pygame.KMOD_CTRL | pygame.KMOD_ALT):
                        text_from_cursor = self.text[self.cursor:]
                        ahead_idx = re.search(r'(?!^)(\b|$)', text_from_cursor).start()
                        self.text = (
                            self.text[:self.cursor] + text_from_cursor[ahead_idx:]
                        )
                    else:
                        self.text = (
                            self.text[:self.cursor] + self.text[self.cursor + 1:]
                        )
                    self.dirty = 1
            elif event.key == pygame.K_LEFT:
                if self.cursor != 0:
                    if event.mod & pygame.KMOD_CTRL:
                        text_until_cursor = self.text[:self.cursor]
                        idx_from_end = re.search(r'(?!^)(\b|$)', text_until_cursor[::-1]).start()
                        self.cursor -= idx_from_end
                    else:
                        self.cursor -= 1
                    self.dirty = 1
            elif event.key == pygame.K_RIGHT:
                if self.cursor != len(self.text):
                    if event.mod & pygame.KMOD_CTRL:
                        text_from_cursor = self.text[self.cursor:]
                        ahead_idx = re.search(r'(?!^)(\b|$)', text_from_cursor).start()
                        self.cursor += ahead_idx
                    else:
                        self.cursor += 1
                    self.dirty = 1
        return False


class Scene:
    def __init__(self, gameloop: 'GameLoop', caption: str) -> None:
        self.gameloop = gameloop
        self.render_group = pygame.sprite.LayeredDirty()
        self.caption = caption

    def update(self) -> None:
        pass

    def render(self, screen: pygame.Surface) -> List[pygame.Rect]:
        pass

    def handle_event(self, event: pygame.event.Event) -> None:
        pass

class MainMenu(Scene):
    def __init__(self, gameloop: 'GameLoop') -> None:
        super().__init__(gameloop, 'WWIIL: Pacific Front')
        ssize = gameloop.screen.get_rect().size
        self.bg = Background('menubg.png', ssize, self.render_group)
        self.gameloop = gameloop
        self.font = pygame.freetype.Font(
            Path(__file__).parent.parent / 'assets' / 'font' / 'CutiveMono-Regular.ttf', 48
        )
        frect = self.font.get_rect('WWII: Pacific Front')
        frect.right = ssize[0] * 14 // 15
        frect.bottom = ssize[1] // 8
        titlepos = frect.topleft
        self.font.render_to(self.bg.image, titlepos, 'WWII: Pacific Front', pygame.Color('Black'))
        brect = pygame.Rect(ssize[0] // 15, ssize[1] // 5 + 50, 200, 50)
        self.buttons = pygame.sprite.Group()
        self.storybutton = Button(
            brect,
            'Story',
            self.font,
            pygame.Color('White'),
            pygame.Color('Navy'),
            lambda: gameloop.change_scene('menu_story'),
            self.render_group, self.buttons
        )
        self.freeplaybutton = Button(
            brect.move(250, 0),
            'Freeplay',
            self.font,
            pygame.Color('White'),
            pygame.Color('Mediumblue'),
            lambda: gameloop.change_scene('menu_freeplay'),
            self.render_group, self.buttons
        )
        self.multiplayerbutton = Button(
            brect.move(0, 75),
            'Multiplayer',
            self.font,
            pygame.Color('White'),
            pygame.Color('Red'),
            lambda: gameloop.change_scene('menu_multiplayer'),
            self.render_group, self.buttons
        )
        self.optionsbutton = Button(
            brect.move(250, 75),
            'Options',
            self.font,
            pygame.Color('Black'),
            pygame.Color('White'),
            lambda: gameloop.change_scene('menu_options'),
            self.render_group, self.buttons
        )
    
    def update(self) -> None:
        self.buttons.update()
    
    def render(self, screen: pygame.Surface) -> List[pygame.Rect]:
        return self.render_group.draw(screen)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.VIDEORESIZE:
            self.resize(event.size)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.gameloop.running = False

    def resize(self, size: Tuple[int, int]) -> None:
        self.bg.resize(size)
        frect = self.font.get_rect('WWII: Pacific Front')
        frect.right = size[0] * 14 // 15
        frect.bottom = size[1] // 8
        titlepos = frect.topleft
        self.font.render_to(self.bg.image, titlepos, None, pygame.Color('Black'))
        brect = pygame.Rect(size[0] // 15, size[1] // 5 + 50, 200, 50)
        self.storybutton.rect = brect
        self.freeplaybutton.rect = brect.move(250, 0)
        self.multiplayerbutton.rect = brect.move(0, 75)
        self.optionsbutton.rect = brect.move(250, 75)
        self.bg.dirty = 1

class StoryMenu(Scene):
    def __init__(self, gameloop: 'GameLoop') -> None:
        super().__init__(gameloop, 'WWII: Pacific Front - Story')
        ssize = gameloop.screen.get_rect().size
        self.bg = Background('menubg.png', ssize, self.render_group)
        self.bg.base_image.fill(pygame.Color('#404040'), special_flags=pygame.BLEND_SUB)
        self.bg.image.fill(pygame.Color('#404040'), special_flags=pygame.BLEND_SUB)

        self.gameloop = gameloop
        self.font = pygame.freetype.Font(
            Path(__file__).parent.parent / 'assets' / 'font' / 'CutiveMono-Regular.ttf', 48
        )
        frect = self.font.get_rect('Story')
        frect.centerx = ssize[0] // 2
        frect.top = 20
        self.bg.image.fill(pygame.Color('Gray16'), pygame.Rect(0, 0, ssize[0], frect.bottom + 20))
        titlepos = frect.topleft
        self.font.render_to(self.bg.image, titlepos, None, pygame.Color('White'))
        brect = pygame.Rect(0, ssize[1] - 100, 200, 50)
        brect.right = ssize[0] // 2 - 25
        self.buttons = pygame.sprite.Group()
        self.startbutton = Button(
            brect,
            'Begin',
            self.font,
            pygame.Color('White'),
            pygame.Color('Navy'),
            lambda: gameloop.change_scene('menu_story'),
            self.render_group, self.buttons
        )
        self.backbutton = Button(
            brect.move(250, 0),
            'Back',
            self.font,
            pygame.Color('Black'),
            pygame.Color('White'),
            lambda: gameloop.change_scene('menu_main'),
            self.render_group, self.buttons
        )
        irect = pygame.Rect(0, 0, 500, 50)
        irect.center = self.bg.rect.center
        self.nameinput = TextInput(
            irect,
            self.font,
            pygame.Color('Black'),
            pygame.Color('White'),
            self.render_group,
            text_size=24
        )

    def update(self) -> None:
        self.buttons.update()
        self.nameinput.update()

    def render(self, screen: pygame.Surface) -> List[pygame.Rect]:
        return self.render_group.draw(screen)

    def handle_event(self, event: pygame.event.Event) -> None:
        self.nameinput.handle_event(event)
        if event.type == pygame.VIDEORESIZE:
            self.resize(event.size)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.gameloop.change_scene('menu_main')

    def resize(self, size: Tuple[int, int]) -> None:
        self.bg.resize(size)
        frect = self.font.get_rect('Story')
        frect.centerx = size[0] // 2
        frect.top = 20
        self.bg.image.fill(pygame.Color('Gray16'), pygame.Rect(0, 0, size[0], frect.bottom + 20))
        titlepos = frect.topleft
        self.font.render_to(self.bg.image, titlepos, None, pygame.Color('White'))
        brect = pygame.Rect(0, size[1] - 100, 200, 50)
        brect.right = size[0] // 2 - 25
        self.startbutton.rect = brect
        self.backbutton.rect = brect.move(250, 0)
        self.nameinput.rect.center = self.bg.rect.center
        self.bg.dirty = 1

class FreeplayMenu(Scene):
    pass

class MultiplayerMenu(Scene):
    pass

class OptionsMenu(Scene):
    pass

class StoryGame(Scene):
    pass

class FreeplayGame(Scene):
    pass

class MultiplayerGame(Scene):
    pass

class GameLoop:
    scenedict = {
        'menu_main': MainMenu,
        'menu_story': StoryMenu,
        'menu_freeplay': FreeplayMenu,
        'menu_multiplayer': MultiplayerMenu,
        'menu_options': OptionsMenu,
        'game_story': StoryGame,
        'game_freeplay': FreeplayGame,
        'game_multiplayer': MultiplayerGame,
    }

    def __init__(self, init_scene: str, size: Tuple[int, int]) -> None:
        self.running = False
        self.screen = pygame.display.set_mode(size, flags=pygame.RESIZABLE)
        self.current_scene: Scene = GameLoop.scenedict[init_scene](self)
        self.clock = pygame.time.Clock()

    def run(self) -> None:
        self.running = True
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: # Catch window close events
                    self.running = False
                else:
                    self.current_scene.handle_event(event)
            self.current_scene.update()
            pygame.display.update(self.current_scene.render(self.screen))
            self.clock.tick(60)
            pygame.display.set_caption(
                f'{self.current_scene.caption} (FPS: {self.clock.get_fps()})'
            )

    def change_scene(self, scene: str):
        self.current_scene = GameLoop.scenedict[scene](self)

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

    firegrid = FiringGrid((30, 30), ShotStyle.CLEAN, ship_group, board_group)
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
