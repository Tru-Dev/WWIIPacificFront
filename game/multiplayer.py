'''
WWII Pacific Front - multiplayer.py
(C) 2021 Jesus Trujillo, Delaney Siggia, Calvin Guela, Anthony Jaimes, Rocco Carrozza
---
This module is responsible for multiplayer capabilities.
'''

import asyncio
import json
import websockets

async def chatClient():
    uri = "ws://wwiipacificfrontserver.tru_dev.repl.co/ws/chat/"
    async with websockets.connect(uri) as websocket:
        await websocket.send(json.dumps({'Greeting': 'Hello!'}))
        print(await websocket.recv())

asyncio.get_event_loop().run_until_complete(chatClient())
