from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

# Define the FormGroups model
class FormGroups(Base):
    __tablename__ = "form_groups"

    id = Column(Integer, primary_key=True, index=True)
    form_id = Column(Integer, ForeignKey("forms.id", ondelete="CASCADE"))
    name = Column(String)
    slug = Column(String(50))
    is_enabled = Column(Boolean, default=True)
    is_add_more = Column(Boolean, default=False)
    order = Column(Integer, nullable=False)
    created_ts = Column(
        DateTime(timezone=True),
        default=datetime.now,
    )
    updated_ts = Column(
        DateTime(timezone=True),
        default=datetime.now,
        onupdate=datetime.now,
    )

    form_group_fields = relationship("FormGroupFields",  cascade="all, delete-orphan", back_populates="form_groups")

    forms = relationship("Forms", back_populates="form_groups")
     
    def to_dict(self):
        return {
            "form_group_id": self.id,
            "form_id": self.form_id,
            "name": self.name.capitalize(),
            "slug": self.slug,
            "is_enabled": self.is_enabled,
            "is_add_more": self.is_add_more,
            "fields": [field.to_dict() for field in sorted(self.form_group_fields, key=lambda f: f.order)],
            "order": self.order,
            "created_ts": self.created_ts,
            "updated_ts": self.updated_ts,
        }