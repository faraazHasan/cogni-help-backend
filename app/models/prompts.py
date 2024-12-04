from datetime import datetime

from sqlalchemy import Column, DateTime, String, Integer, Text

from app.database import Base


# Define the Journal model
class Prompts(Base):
    __tablename__ = "prompts"

    id = Column(Integer, primary_key=True, index=True)
    prompt_type = Column(String(25))
    prompt = Column(Text)
    created_ts = Column(
        DateTime(timezone=True),
        default=datetime.now,
    )
    updated_ts = Column(
        DateTime(timezone=True),
        default=datetime.now,
        onupdate=datetime.now,
    )
