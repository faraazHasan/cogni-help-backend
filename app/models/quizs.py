from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer

from app.database import Base
from sqlalchemy import Enum as sqEnum
from sqlalchemy.orm import relationship

# Define the Quizes model
class Quizs(Base):
    __tablename__ = "quizs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    status: sqEnum = Column(sqEnum("pending", "completed"), nullable=False)
    current_question_id = Column(
        Integer,
        nullable=True,
    )
    date_completed = Column(
        DateTime(timezone=True),
        nullable=True
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

    # users = relationship("User", back_populates="quizs")
    questions = relationship("Questions", back_populates="quizs")

    def to_dict(self):
        current_question_index = None

        sorted_questions = []

        if self.current_question_id and self.questions:
            sorted_questions = sorted(
                self.questions, key=lambda question: question.id)
            for index, question in enumerate(sorted_questions):
                if question.id == self.current_question_id:
                    current_question_index = index
                    break
        return {
            "id": self.id,
            "quiz_id": self.id,
            "user_id": self.user_id,
            "status": self.status,
            "current_question_id": self.current_question_id,
            "date_completed": self.date_completed,
            "created_ts": self.created_ts,
            "updated_ts": self.updated_ts,
            "questions": [question.selected_data() for question in sorted_questions],
            "current_question_index": current_question_index,
        }
