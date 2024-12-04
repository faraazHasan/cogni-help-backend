from typing import List, Optional
from pydantic import BaseModel


class FieldSchema(BaseModel):
    field_id: Optional[int] = None
    form_group_id: Optional[int] = None
    field_type: str
    field_name: str
    is_enabled: bool
    is_add_more: bool
    is_required: bool
    slug: str
    order: int
    options: Optional[List[str]] = None
    created_ts: Optional[str] = None
    updated_ts: Optional[str] = None


class FormGroupSchema(BaseModel):
    form_group_id: Optional[int] = None
    form_id: Optional[int] = None
    fields: List[FieldSchema]
    is_add_more: bool
    is_enabled: bool
    slug: str
    name: str
    order: int
    created_ts: Optional[str] = None
    updated_ts: Optional[str] = None


class FormBuilderSchema(BaseModel):
    form_id: Optional[int] = None
    name: str
    is_enabled: bool
    form_groups: List[FormGroupSchema]
    created_ts: Optional[str] = None
    updated_ts: Optional[str] = None
