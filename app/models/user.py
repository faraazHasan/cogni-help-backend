from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey
from sqlalchemy import Enum as sqEnum
from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base

# Define the User model
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("company.id"))
    first_name = Column(String(50))
    last_name = Column(String(50))
    phone = Column(String, nullable=True)
    image = Column(String, nullable=True)
    email = Column(
        String,
        unique=True,
    )
    account_type: sqEnum = Column(sqEnum("user", "admin"), nullable=False)
    password = Column(
        String,
    )
    is_active = Column(
        Boolean,
        default=False,
    )
    is_verified = Column(
        Boolean,
        default=False,
    )
    verification_code = Column(Text, nullable=True)
    last_login = Column(DateTime(timezone=True), nullable=True)
    country_code = Column(String, nullable=True)
    created_ts = Column(
        DateTime(timezone=True),
        default=datetime.now,
    )
    updated_ts = Column(
        DateTime(timezone=True),
        default=datetime.now,
        onupdate=datetime.now,
    )
    company = relationship("Company", back_populates="users")
    # quizes = relationship("Quizs", back_populates="users")
    user_detail = relationship("UserDetails", back_populates="user", uselist=False)
    user_sessions = relationship("UserSession", back_populates="user")

    def to_dict(self):
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "image": self.image,
            "phone": self.phone,
            "email": self.email,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "account_type": self.account_type,
            "verification_code": self.verification_code,
            "last_login": self.last_login,
            "country_code": self.country_code,
            "user_detail": self.user_detail.to_dict() if self.user_detail else None,
            "created_ts": self.created_ts,
            "updated_ts": self.updated_ts,
        }
