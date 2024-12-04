from app.features.form_builder.schemas import  FieldSchema, FormGroupSchema
from sqlalchemy.orm import Session
from app.models.form_groups import FormGroups
from app.models.form_group_fields import FormGroupFields

def add_form_group(db: Session,form_id: int, form_group: FormGroupSchema ):
    form_group_data = FormGroups(
        form_id=form_id,
        name=form_group.name.lower(),
        slug=form_group.slug,
        order = form_group.order,
        is_add_more=form_group.is_add_more,
        is_enabled=form_group.is_enabled,
    )
    db.add(form_group_data)
    db.flush()
    return form_group_data.id

def add_fields(db: Session,form_group_id: int, field: FieldSchema ):
    new_fields = FormGroupFields(
        form_group_id=form_group_id,
        field_type=field.field_type,
        field_name=field.field_name.lower(),
        options=field.options,
        slug=field.slug,
        order = field.order,
        is_add_more=field.is_add_more,
        is_required=field.is_required,
        is_enabled=field.is_enabled,
    )
    db.add(new_fields)
    db.flush()
    return new_fields.id