import logging
import re
from collections.abc import AsyncGenerator
from datetime import datetime
from typing import Optional
from uuid import uuid4

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class WebSocketResponse:
    """
    A class that handles writing messages for the bot.
    """

    def __init__(
        self,
        *,
        user_id: str,
        websocket: WebSocket,
        connection_manager=None,
    ):
        self.connection_manager = connection_manager
        self.user_id = user_id
        self.websocket = websocket

    async def async_word_generator(self, text: str) -> AsyncGenerator[str, None]:
        """Async generator yielding words from the given text."""
        words = re.split(r"(\s+)", text)
        for word in words:
            yield word

    # Websocket Sending
    async def create_bot_response(
        self, text: AsyncGenerator[str, None] | str
    ) -> Optional[str]:
        """Creates bot message and sends it. Returns full text."""
        now = datetime.utcnow()
        current_time = now.strftime("%H:%M")
        final_text = ""
        uuid = str(uuid4())
        if not text:
            logger.error(f"Could not generate text for {self.user_id}")
            await self.connection_manager.send_personal_message(
                self.websocket,
                {
                    "mt": "message_upload_confirm",
                    "chatId": self.user_id,
                    "uuid": uuid,
                    "message": "I'm having difficulty comprehending your message."
                    " Could you please phrase it differently?",
                    "time": current_time,
                    "isBot": True,
                },
            )
            return None

        if self.connection_manager is None:
            logger.error("Websocket is not initialized.")
            return None

        await self.connection_manager.send_personal_message(
            self.websocket,
            {
                "mt": "chat_message_bot_partial",
                "chatId": self.user_id,
                "start": uuid,
            },
        )

        if isinstance(text, str):
            text = self.async_word_generator(text)

        async for t in text:
            if t:
                final_text += t
                await self.connection_manager.send_personal_message(
                    self.websocket,
                    {
                        "mt": "chat_message_bot_partial",
                        "chatId": self.user_id,
                        "uuid": uuid,
                        "partial": t,
                    },
                )

        await self.connection_manager.send_personal_message(
            self.websocket,
            {
                "mt": "chat_message_bot_partial",
                "chatId": self.user_id,
                "stop": uuid,
            },
        )

        await self.connection_manager.send_personal_message(
            self.websocket,
            {
                "mt": "message_upload_confirm",
                "chatId": self.user_id,
                "uuid": uuid,
                "message": final_text,
                "time": current_time,
                "isBot": True,
            },
        )
        return final_text
