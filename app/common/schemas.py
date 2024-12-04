from typing import Any, Optional

from pydantic import BaseModel


class ResponseModal(BaseModel):
    success: bool
    message: str
    data: Optional[Any | None] = None
    error: Optional[str] = None
