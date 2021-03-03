'''
WWII Pacific Front Server - main.py
(C) 2021 Jesus Trujillo, Delaney Siggia, Calvin Guela, Anthony Jaimes, Rocco Carrozza
---
This module is the entry point for the game server.
'''

import asyncio
import json
from typing import Type

import websockets

class WSServer:
    def __init__(self, ws: websockets.WebSocketServer, path: str) -> None:
        self.ws = ws
        self.path = path

    async def send(self, msg_type: str, data: dict) -> None:
        await self.ws.send(json.dumps({'type': msg_type, 'data': data}))

    async def recv(self) -> dict:
        return json.loads(await self.ws.recv())

    async def server(self) -> None:
        pass


class WSServerRunner:
    def __init__(
        self,
        ws_server_class: Type[WSServer],
        host: str='0.0.0.0',
        port: int=8000
    ) -> None:
        self.ws_server_class = ws_server_class
        self.start_server = websockets.serve(self.server, host, port)

    async def server(self, ws: websockets.WebSocketServer, path: str) -> None:
        server_instance = self.ws_server_class(ws, path)
        await server_instance.server()
    
    def run(self) -> None:
        try:
            asyncio.get_event_loop().run_until_complete(self.start_server)
            asyncio.get_event_loop().run_forever()
        except KeyboardInterrupt:
            pass


class ChatServer(WSServer):
    async def server(self) -> None:
        while True:
            recv = await self.recv()
            print(recv)
            await self.send('echo', recv)


runner = WSServerRunner(ChatServer)

runner.run()
