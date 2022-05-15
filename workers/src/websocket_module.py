import asyncio
import websockets


class WebSocketNotifier:
    connections = {}

    def __init__(self, port = 8765, address = "0.0.0.0"):
        self.port = port
        self.address = address

    async def connect(self):
        await websockets.serve(self.register, self.address, self.port)
            # await asyncio.Future()

    async def register(self, websocket, user_id):
        self.connections[user_id] = websocket
        try:
            await websocket.wait_closed()
        finally:
            self.connections[user_id].remove(websocket)

    async def send_notify(self, user_id, notify_message):
        self.connections[user_id].send(notify_message)
