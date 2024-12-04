import asyncio
import logging
from datetime import datetime

from fastapi import Depends
from sqlalchemy.orm import Session

from app.database import db_connection
from app.features.bot.repository import add_daily_journal

from .utils.response import ResponseCreator
from .websocket_response import WebSocketResponse

logger = logging.getLogger(__name__)


def printf(*arg, **kwarg):
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(timestamp)


class BotMessage:
    """
    A class that handles writing messages for the bot.
    """

    def __init__(
        self,
        *,
        socket_response: WebSocketResponse,
        user_id: str | None,
        db: Session = Depends(db_connection),
    ):
        self.socket_response = socket_response
        self.user_id = user_id
        self.db = db
        self.intermediate_message_sent = False
        self.intermediate_message_time = None

    # Main Bot Message Sending
    async def send_bot_message(self, text: str) -> bool:
        """
        Sends a bot message to the user
        :param text: the text the user sent
        :returns: whether the bot has sent the response or not
        """
        # Task for handling the main bot logic
        is_answer_found_and_sent_main_task = asyncio.create_task(self.bot_handler(text))

        is_answer_found_and_sent = await is_answer_found_and_sent_main_task
        return is_answer_found_and_sent

    # Bot Handler
    async def bot_handler(self, user_input: str) -> bool:
        try:
            """
            Respond to the user input, optimizing the process of querying GPT-4.
            :param user_input: Text input from the user
            :return: Boolean indicating if the bot has responded or not
            """

            gpt_resp = await ResponseCreator().generate_summary(user_input)
            summary = await self.socket_response.create_bot_response(
                gpt_resp,
            )
            if summary != "Sorry, we cannot generate a summary.":
                asyncio.create_task(
                    add_daily_journal(self.user_id, summary, user_input, self.db)
                )
            return False

        except Exception as e:
            print(e, "Bot Handler error")
            # Return True indicating the bot has not provided a response
            return True
