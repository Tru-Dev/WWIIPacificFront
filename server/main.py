'''
WWII Pacific Front Server - main.py
(C) 2021 Jesus Trujillo, Delaney Siggia, Calvin Guela, Anthony Jaimes, Rocco Carrozza
---
This module is the entry point for the game server.
'''

import asyncio
import json
import websockets

async def echo(websocket, path):
    async for message in websocket:
        print(json.loads(message))
        await websocket.send(message)

start_server = websockets.serve(echo, "0.0.0.0", 3000)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
