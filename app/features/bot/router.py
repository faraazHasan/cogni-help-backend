import asyncio
import json
from datetime import datetime

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.websockets import WebSocketState
from jose import jwe, jwt

from app.config import env_variables
from app.database import db_connection
from app.features.aws.secretKey import get_secret_keys
from app.features.bot.message import BotMessage
from app.features.bot.schemas import MessageData, MessageUploadData
from app.features.bot.websocket_response import WebSocketResponse

env_data = env_variables()
keys = get_secret_keys()


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def send_personal_message(self, websocket: WebSocket, message: dict):
        if websocket.client_state == WebSocketState.CONNECTED:
            await websocket.send_text(json.dumps(message))

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            if connection.client_state == WebSocketState.CONNECTED:
                await connection.send_text(json.dumps(message))


manager = ConnectionManager()

router = APIRouter(tags=["Chat"], prefix="/chat")


@router.websocket("/ws/connection/")
async def websocket_endpoint(websocket: WebSocket):
    try:
        await connect_websocket(websocket)
        now = datetime.utcnow()
        current_time = now.strftime("%H:%M")
        isError = False

        while True:
            data = await websocket.receive_text()
            await process_received_data(data, current_time, isError, websocket)

    except WebSocketDisconnect:
        await handle_websocket_disconnect(websocket, current_time)
    except Exception as e:
        print("error handle_message_upload", e)


async def connect_websocket(websocket: WebSocket):
    await manager.connect(websocket)


async def process_received_data(data, current_time, isError, websocket):
    received_data = json.loads(data)
    mt = received_data.get("mt", "")

    if mt == "message_upload" and not isError:
        await handle_message_upload(received_data, current_time, websocket)


async def handle_message_upload(received_data, current_time, websocket):
    socket_response = WebSocketResponse(
        websocket=websocket,
        connection_manager=manager,
        user_id=None,
    )
    try:
        db = next(db_connection())
        upload_data = MessageUploadData(**received_data)
        message = MessageData(
            time=current_time,
            message=upload_data.message,
            isBot=upload_data.isBot,
            token=upload_data.token,
            mt="message_upload_confirm",
        )

        await manager.send_personal_message(websocket, message.dict())

        if upload_data.token:
            jwt_token = jwe.decrypt(str(upload_data.token), "asecret128bitkey")
            payload = jwt.decode(
                jwt_token,
                keys["SECRET_KEY"],
                algorithms=keys["ALGORITHM"],
            )
            user_id = payload.get("id")

            socket_response = WebSocketResponse(
                websocket=websocket,
                connection_manager=manager,
                user_id=user_id,
            )

            bot_message = BotMessage(
                socket_response=socket_response, user_id=user_id, db=db
            )
            no_answer_found = await bot_message.send_bot_message(
                received_data["message"]
            )

            await asyncio.sleep(1)

            if no_answer_found:
                default_answer = "Sorry, we cannot generate a summary."
                message = MessageData(
                    time=current_time,
                    message=default_answer,
                    isBot=True,
                    mt="message_upload_confirm",
                )
                await manager.send_personal_message(websocket, message.dict())
        else:
            await socket_response.create_bot_response(
                f"Please login again your token is expired."
            )
    except Exception as e:
        print("error in handle_message_upload", e)
        if socket_response:
            await socket_response.create_bot_response(
                f"Please try after sometime or please login again."
            )


async def handle_websocket_disconnect(websocket: WebSocket, current_time):
    manager.disconnect(websocket)
    message = {"time": current_time, "message": "Offline"}
    try:
        await manager.broadcast(message)
    except Exception as e:
        print(e, "error in handle_websocket_disconnect", e)
