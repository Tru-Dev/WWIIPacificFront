'''
WWII Pacific Front - multiplayer.py
(C) 2021 Jesus Trujillo, Delaney Siggia, Calvin Guela, Anthony Jaimes, Rocco Carrozza
---
This module is responsible for multiplayer capabilities.
'''

import asyncio
import json
from typing import Any, MutableSequence, Optional

import websockets
import pygame
import pygame.event
import pygame.key
import pygame.display
import pygame.freetype
import pygame.sprite

from .pygame_async_utils import AsyncClock


class WSClientMixin:
    def __init__(self, *args, uri: str, ssl: Any, **kwargs) -> None:
        self.ws = asyncio.get_event_loop().run_until_complete(websockets.connect(uri, ssl=ssl))
        super().__init__(*args, **kwargs)

    async def send(self, msg_type: str, data: dict) -> None:
        await self.ws.send(json.dumps({'type': msg_type, 'data': data}))

    async def recv(self) -> dict:
        return json.loads(await self.ws.recv())
    
    async def client(self) -> None:
        pass

    def run(self) -> None:
        asyncio.get_event_loop().run_until_complete(self.client())


class ChatClient(WSClientMixin):
    def __init__(self, uri: str='wss://wwiipacifront.trudev.tech/ws/chat/', ssl: Any=True) -> None:
        super().__init__(uri=uri, ssl=ssl)

    async def client(self) -> None:
        nick = input('Enter a Nickname: ')
        await self.send('nickname', {'nickname': nick})
        print('Server Response:', await self.recv())

        while True:
            print('Received Data from Server:', await self.recv())

    def run(self) -> None:
        try:
            super().run()
            asyncio.get_event_loop().run_forever()
        except KeyboardInterrupt:
            print('Closing Socket...')
            asyncio.get_event_loop().run_until_complete(self.ws.close())



class UIElement(pygame.sprite.DirtySprite):
    def __init__(self, rect: pygame.Rect, container: Optional['UIContainer']) -> None:
        super().__init__()
        self.rect = rect
        self.image = pygame.Surface(rect.size)
        self.parent = container

    @property
    def parent(self):
        return self._parent
    
    @parent.setter
    def parent(self, container: 'UIContainer'):
        self.add(container)
        self._parent = container

    def render(self) -> None:
        pass


class RenderedUIContainer(UIElement):
    def __init__(
        self,
        owner: 'UIContainer',
        parent_container: Optional['UIContainer'],
        bg_color: pygame.Color
    ) -> None:
        super().__init__(owner.rect, parent_container)
        self.owner = owner
        self.parent = parent_container
        self.bg_color = bg_color
        self.image = pygame.Surface(owner.rect.size, flags=pygame.SRCALPHA)
        self.render()
    
    def render(self) -> None:
        self.image.fill(self.bg_color)
        self.owner.draw()


class UIContainer(pygame.sprite.LayeredDirty):
    def __init__(
            self,
            rect: pygame.Rect,
            parent_container: Optional['UIContainer'],
            *ui_elements: UIElement,
            ui_containers: MutableSequence['UIContainer']=[],
            bg_color: pygame.Color=pygame.Color(0, 0, 0, 0),
            **kwargs
        ):
        super().__init__(*ui_elements, **kwargs)
        self.rect = rect
        self.rendered = RenderedUIContainer(self, parent_container, bg_color)
        self.ui_containers = ui_containers
        for c in ui_containers:
            self.add(c.rendered)
        if parent_container is not None:
            parent_container.add_container(self)
        self.parent = parent_container

    def update(self, *args, **kwargs) -> None:
        super().update(*args, **kwargs)
        for c in self.ui_containers:
            c.update(*args, **kwargs)

    def render(self):
        self.rendered.image.fill(self.rendered.bg_color)
        self.draw(self.rendered.image)

    def add_container(self, ui_container: 'UIContainer'):
        self.ui_containers.append(ui_container)

    def propagate_dirty(self):
        self.rendered.dirty = 1
        if self.parent is not None:
            self.parent.propagate_dirty()


class RenderedUIRoot(RenderedUIContainer):
    def __init__(self, owner: 'UIRoot', screen_surface: pygame.Surface) -> None:
        super().__init__(owner, None)
        screen_surface.blit(self.image, (0, 0))
        self.image = screen_surface


class UIRoot(UIContainer):
    def __init__(
        self,
        screen_surface: pygame.Surface,
        *ui_elements: UIElement,
        ui_containers: MutableSequence[UIContainer]=[],
        **kwargs
    ):
        super().__init__(
            screen_surface.get_rect(), None, *ui_elements, ui_containers=ui_containers, **kwargs
        )
        self.rendered = RenderedUIRoot(self, screen_surface)


class PostedMessages(UIContainer):
    def __init__(
        self,
        rect: pygame.Rect,
        parent_container: UIContainer,
        *messages: 'Message',
        **kwargs
    ):
        super().__init__(rect, parent_container, *messages, **kwargs)

    def update(self, *args, **kwargs) -> None:
        super().update(*args, **kwargs)
        self.propagate_dirty()


class Message(UIElement):
    def __init__(self, container: Optional[PostedMessages]) -> None:
        super().__init__(pygame.Rect(0, 0, 1, 1), container)


class PyGameChatClient(WSClientMixin, UIContainer):
    def __init__(self, uri: str='wss://wwiipacifront.trudev.tech/ws/chat/', ssl: Any=True) -> None:
        super().__init__(uri=uri, ssl=ssl)
        

    async def client(self) -> None:
        pass

    def run(self) -> None:
        super().run()
        try:
            asyncio.get_event_loop().run_forever()
        except KeyboardInterrupt:
            print('Closing Socket...')
            asyncio.get_event_loop().run_until_complete(self.ws.close())


