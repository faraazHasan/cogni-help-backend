from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Text

from app.database import Base


# Define the Journal model
class Journal(Base):
    __tablename__ = "journal"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    journal_details = Column(Text)
    journal_summary = Column(Text)
    is_questions_generated = Column(
        Boolean,
        nullable=True,
    )
    created_ts = Column(
        DateTime(timezone=True),
        default=datetime.now,
    )
    updated_ts = Column(
        DateTime(timezone=True),
        default=datetime.now,
        onupdate=datetime.now,
    )

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "journal_summary": self.journal_summary,
            "journal_details": self.journal_details,
            "created_ts": self.created_ts,
            "updated_ts": self.updated_ts,
        }
