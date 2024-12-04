from app.database import Base
from sqlalchemy import Boolean, Column, DateTime, Integer, String
from datetime import datetime
from sqlalchemy.orm import relationship


# Model for the 'company' table in the database
# This model defines the structure for storing company details,
# including name, address, email, and flags like admin and is_active.


class Company(Base):
    __tablename__ = "company"

    id = Column(Integer, primary_key=True, index=True) 
    name = Column(String(50), nullable=True) 
    address = Column(String(255), nullable=True) 
    email = Column(String(50), nullable=True) 
    admin = Column(Boolean, default=False)
    is_active = Column(
        Boolean, default=True
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

    users = relationship("User", back_populates="company")
