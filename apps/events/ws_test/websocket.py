import asyncio
import json
import random
import time
import websockets

clients = set()

def now():
    return int(time.time() * 1000)


async def register(ws):
    clients.add(ws)
    await broadcast_connection_count()


async def unregister(ws):
    clients.remove(ws)
    await broadcast_connection_count()


async def broadcast(data):
    if not clients:
        return
    message = json.dumps(data)
    await asyncio.gather(*(c.send(message) for c in clients))


async def broadcast_connection_count():
    await broadcast({
        "type": "connection_count",
        "connections": len(clients),
        "timestamp": now()
    })


async def event_generator():
    global event_counter

    while True:
        await asyncio.sleep(1)

        event = {
            "type": "item_transfer",
            "timestamp": now(),
            "system_id": random.choice(['ABC', 'DEF', 'GHI']) + "-" + str(random.randint(100, 999)),
            "data": {
                "ownerName": "Player" + str(random.randint(1, 1000)),
                "itemName": "Item" + str(random.randint(1, 1000)),
                "quantity": random.randint(1, 100)
            }
        }

        await broadcast(event)


async def handler(ws):
    await register(ws)

    try:
        async for _ in ws:
            pass
    finally:
        await unregister(ws)


async def main():
    async with websockets.serve(handler, "0.0.0.0", 8765):
        print("WebSocket server running on ws://localhost:8765")
        await event_generator()


asyncio.run(main())