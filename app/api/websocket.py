import json
from fastapi import WebSocket, WebSocketDisconnect
from typing import List

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print("New client connected.")

        # Send welcome message
        welcome_message = {
            "type": "welcome",
            "payload": "Welcome to the WebSocket server!"
        }
        await websocket.send_text(json.dumps(welcome_message))

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        print("Client disconnected.")

    async def broadcast(self, message: dict):
        data = json.dumps(message)
        for connection in self.active_connections:
            if connection.client_state.value == 1:  # WebSocketState.CONNECTED
                await connection.send_text(data)

manager = ConnectionManager()

async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                parsed_message = json.loads(data)
                broadcast_message = {
                    "type": "broadcast",
                    "payload": parsed_message.get("payload")
                }
                await manager.broadcast(broadcast_message)
            except json.JSONDecodeError as e:
                print(f"❌ Error parsing message: {e}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
