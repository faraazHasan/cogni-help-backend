from datetime import datetime

from pydantic import BaseModel


class MessageUploadData(BaseModel):
    mt: str
    isBot: bool
    message: str
    token: str | None


class MessageData(BaseModel):
    time: str
    message: str
    isBot: bool
    mt: str
    token: str | None


class MessageResponse(BaseModel):
    id: int
    created: datetime
    text: str
    file: str
    isBot: bool


class CreateChatId(BaseModel):
    time: str
    clientId: str
    message: str
    isBot: bool
    mt: str
