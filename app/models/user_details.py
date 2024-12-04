from datetime import datetime

from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base

# Define the UserDetails model
class UserDetails(Base):
    __tablename__ = "user_details"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    gender = Column(String, nullable=True)
    notification = Column(Boolean, nullable=True)
    field_of_study = Column(String, nullable=True)
    fcm_token = Column(String, nullable=True)
    address = Column(String, nullable=True)
    dob = Column(Date, nullable=True)
    answer_count = Column(Integer, nullable=True)
    question_set = Column(Integer, nullable=True)
    profile_summary = Column(Text, nullable=True)
    journal_summary = Column(Text, nullable=True)
    quiz_summary = Column(Text, nullable=True)
    is_profile_questions_generated = Column(
        Boolean,
        default=False,
    )
    js_lastupdated = Column(DateTime(timezone=True), nullable=True)
    qs_lastupdated = Column(DateTime(timezone=True), nullable=True) 
    ps_lastupdated = Column(DateTime(timezone=True), nullable=True)
    created_ts = Column(
        DateTime(timezone=True),
        default=datetime.now,
    )
    updated_ts = Column(
        DateTime(timezone=True),
        default=datetime.now,
        onupdate=datetime.now,
    )

    user = relationship(
        "User",
        back_populates="user_detail",
        cascade="all, delete-orphan",
        single_parent=True,
    )

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "gender": self.gender,
            "notification": self.notification,
            "field_of_study": self.field_of_study,
            "fcm_token": self.fcm_token,
            "address": self.address,
            "dob": self.dob,
            "is_profile_questions_generated":self.is_profile_questions_generated,
            "answer_count": self.answer_count,
            "question_set": self.question_set,
            "created_ts": self.created_ts,
            "updated_ts": self.updated_ts,
            "profile_summary": self.profile_summary,
            "journal_summary": self.journal_summary,
            "quiz_summary": self.quiz_summary
        }
