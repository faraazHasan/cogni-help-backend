from sqlalchemy import Boolean, Column, DateTime, Integer, String
from app.database import Base
from datetime import datetime
from sqlalchemy.orm import relationship

class Forms(Base):
    __tablename__ = "forms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=True)
    is_enabled = Column(Boolean, default=True)
    created_ts = Column(
        DateTime(timezone=True),
        default=datetime.now,
    )
    updated_ts = Column(
        DateTime(timezone=True),
        default=datetime.now,
        onupdate=datetime.now,
    )

    form_groups = relationship("FormGroups", cascade="all, delete-orphan", back_populates="forms")

    def to_dict(self):
        return {
            "form_id": self.id,
            "name": self.name.capitalize(),
            "is_enabled": self.is_enabled,
            "form_groups": [form_group.to_dict() for form_group in sorted(self.form_groups, key=lambda f: f.order)],
            "created_ts": self.created_ts,
            "updated_ts": self.updated_ts,
        }