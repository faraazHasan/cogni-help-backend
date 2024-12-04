from sqlalchemy import TEXT, Boolean, Column, DateTime, ForeignKey, Integer, String
from app.database import Base
from datetime import datetime
from sqlalchemy.orm import relationship


# Define the GroupFields model
class FormGroupFields(Base):
    __tablename__ = "form_group_fields"

    id = Column(Integer, primary_key=True, index=True)
    form_group_id = Column(Integer, ForeignKey("form_groups.id", ondelete="CASCADE"))
    field_type = Column(String(15), nullable=True)
    field_name = Column(String(50), nullable=True)
    options = Column(TEXT, nullable=True)
    slug = Column(String(50))
    is_enabled = Column(Boolean, default=True)
    is_add_more = Column(Boolean, default=False)
    is_required = Column(Boolean, default=False)
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

    form_groups = relationship("FormGroups", back_populates="form_group_fields")

    def to_dict(self):
        options = self.options
        def convert_to_list(options):
            if isinstance(options, str):
                try:
                    # Remove curly braces
                    options = options.strip('{}')
                    
                    # Split by commas and strip each part of leading/trailing spaces and quotes
                    options_list = [opt.strip().strip('"') for opt in options.split(',') if opt.strip()]
                    
                    # Return only if there are valid options, otherwise return an empty list
                    return options_list if options_list else []
                except Exception as e:
                    print(f"Error converting options: {e}")
                    return []
            
            return []
        return {
            "field_id": self.id,
            "form_group_id": self.form_group_id,
            "field_name": self.field_name.capitalize(),
            "field_type": self.field_type,
            "slug": self.slug,
            "options": convert_to_list(options),
            "is_required": self.is_required,
            "is_enabled": self.is_enabled,
            "is_add_more": self.is_add_more,
            "order": self.order,
            "created_ts": self.created_ts,
            "updated_ts": self.updated_ts,
        }