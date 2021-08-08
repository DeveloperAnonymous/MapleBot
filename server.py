import asyncio
import datetime
import random

import websockets

import configs

"""
Test server to test the websockets locally
"""

async def time(websocket, path):
    while True:
        now = datetime.datetime.utcnow().isoformat() + "Z"
        await websocket.send(now)
        await asyncio.sleep(random.random() * 3)


start_server = websockets.serve(time, configs.WS_HOST, configs.WS_PORT)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
