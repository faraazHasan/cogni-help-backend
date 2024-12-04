from datetime import datetime
import json
import random

from sqlalchemy import Boolean, Column, DateTime
from sqlalchemy import ForeignKey, Integer, Text
from sqlalchemy.orm import relationship

from app.database import Base

# Define the Questions model
class Questions(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    quiz_id = Column(Integer, ForeignKey("quizs.id"))
    details = Column(Text, nullable=True)
    options = Column(Text, nullable=True)
    correct_answer = Column(Text, nullable=True)
    user_answer = Column(Text, nullable=True)
    hint = Column(Text, nullable=True)
    is_answered = Column(
        Boolean,
        default=False,
    )

    is_abandoned = Column(
        Boolean,
        default=False,
    )
    is_answer_correct = Column(
        Boolean,
        default=False,
    )
    start_datetime = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    end_datetime = Column(
        DateTime(timezone=True),
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

    quizs = relationship("Quizs", back_populates="questions")

    def data(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "quiz_id": self.quiz_id,
            "details": self.details,
            "options": json.loads(self.options),
            "correct_answer": self.updated_ts,
            "user_answer": self.user_answer,
            "hint": self.hint,
            "is_answered": self.created_ts,
            "is_abandoned": self.updated_ts,
            "is_answer_correct": self.is_answer_correct,
            "start_datetime": self.start_datetime,
            "end_datetime": self.end_datetime,
            "created_ts": self.created_ts,
            "updated_ts": self.updated_ts
        }

    def selected_data(self, reduce_options=None):

        def get_options(options_json, reduce_options):
            # Parse the JSON string
            options_data = json.loads(options_json)

            # Extract only the "option" field
            options = [opt["option"] for opt in options_data]

            if not reduce_options:
                return options

            # Ensure the correct answer is included and randomly reduce to 50%
            correct_option = next(opt["option"]
                                  for opt in options_data if opt.get("is_correct"))
            other_options = [opt for opt in options if opt != correct_option]

            # Calculate target length (50% of the original options)
            target_length = len(options) // 2

            # Combine correct answer with other random options
            selected_options = [correct_option] + \
                random.sample(other_options, target_length - 1)

            return selected_options

        return {
            "question_id": self.id,
            "details": self.details,
            "options": get_options(self.options, reduce_options),
            "user_answer": self.user_answer,
            "hint": self.hint,
            "is_answered": self.is_answered,
            "is_abandoned": self.is_abandoned,
            "start_datetime": self.start_datetime,
            "end_datetime": self.end_datetime,
            "show_hint": False,
            "created_ts": self.created_ts,
        }
