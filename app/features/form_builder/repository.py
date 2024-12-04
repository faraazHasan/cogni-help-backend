from sqlalchemy.orm import Session
from app.common import constants
from app.features.form_builder.schemas import FormBuilderSchema
from app.utils.contexts.common_contexts import process_request
from app.models.forms import Forms
from app.models.form_groups import FormGroups
from app.models.form_group_fields import FormGroupFields
from .utils import add_form_group, add_fields


class FormBuilderRepo:
    def __init__(self, db: Session):
        self.db = db

    async def create_form(self, request: FormBuilderSchema):
        with process_request():
            form = (
                self.db.query(Forms).filter(Forms.name == request.name.lower()).first()
            )
            if form:
                return {"message": constants.FORM_EXISTS, "success": False}

            new_form = Forms(
                name=request.name.lower(),
                is_enabled=request.is_enabled,
            )
            self.db.add(new_form)
            self.db.flush()  # Persist changes
            for form_group in request.form_groups:
                form_group_data = FormGroups(
                    form_id=new_form.id,
                    name=form_group.name.lower(),
                    slug=form_group.slug,
                    order=form_group.order,
                    is_add_more=form_group.is_add_more,
                    is_enabled=form_group.is_enabled,
                )
                self.db.add(form_group_data)
                self.db.flush()
                for field in form_group.fields:
                    new_fields = FormGroupFields(
                        form_group_id=form_group_data.id,
                        field_type=field.field_type,
                        field_name=field.field_name.lower(),
                        options=field.options,
                        slug=field.slug,
                        order=field.order,
                        is_add_more=field.is_add_more,
                        is_required=field.is_required,
                        is_enabled=field.is_enabled,
                    )
                    self.db.add(new_fields)

            return {"message": constants.FORM_CREATED, "success": True, "data": request}

    async def update_form(self, request: FormBuilderSchema):
        with process_request():
            form_group_ids = []
            field_ids = []

            form = self.db.query(Forms).filter(Forms.id == request.form_id).first()

            if not form:
                return {
                    "message": f"Form '{request.name}' does not exist",
                    "success": False,
                }
            form.name = request.name
            form.is_enabled = request.is_enabled
            self.db.flush()

            for form_group in request.form_groups:
                if form_group.form_group_id:
                    form_group_ids.append(form_group.form_group_id)
                    fg = (
                        self.db.query(FormGroups)
                        .filter(FormGroups.id == form_group.form_group_id)
                        .first()
                    )

                    if not fg:
                        return {
                            "message": f"Form group '{form_group.name}' does not exist",
                            "success": False,
                        }

                    # Update existing form group
                    fg.name = form_group.name.lower()
                    fg.slug = form_group.slug
                    fg.order = form_group.order
                    fg.is_enabled = form_group.is_enabled
                    fg.is_add_more = form_group.is_add_more

                    self.db.flush()

                    # Handle form group fields
                    for field in form_group.fields:
                        if field.field_id:
                            field_ids.append(field.field_id)
                            f = (
                                self.db.query(FormGroupFields)
                                .filter(FormGroupFields.id == field.field_id)
                                .first()
                            )

                            if not f:
                                return {
                                    "message": f"Field '{field.field_name}' does not exist",
                                    "success": False,
                                }

                            # Update existing field
                            f.field_name = field.field_name.lower()
                            f.field_type = field.field_type
                            f.options = field.options
                            f.slug = field.slug
                            f.order = field.order
                            f.is_enabled = field.is_enabled
                            f.is_add_more = field.is_add_more
                            f.is_required = field.is_required

                            self.db.flush()
                        else:
                            # Add new field
                            new_field_id = add_fields(self.db, fg.id, field)
                            field_ids.append(new_field_id)

                else:
                    # Add new form group
                    form_group_id = add_form_group(self.db, request.form_id, form_group)
                    form_group_ids.append(form_group_id)

                    # Add fields for the new form group
                    for field in form_group.fields:
                        # Use form_group_id here
                        new_field_id = add_fields(self.db, form_group_id, field)
                        field_ids.append(new_field_id)

            # Delete FormGroupFields that are not in the field_ids list and belong to the specific form_id
            self.db.query(FormGroupFields).filter(
                FormGroupFields.form_group_id.in_(
                    self.db.query(FormGroups.id).filter(
                        FormGroups.form_id == request.form_id
                    )
                ),
                ~FormGroupFields.id.in_(field_ids),
            ).delete(synchronize_session=False)

            # Delete FormGroups that are not in the form_group_ids list and belong to the specific form_id
            self.db.query(FormGroups).filter(
                FormGroups.form_id == request.form_id,
                ~FormGroups.id.in_(form_group_ids),
            ).delete(synchronize_session=False)

            return {"message": constants.FORM_UPDATED, "success": True, "data": request}

    async def get_form(self, form_id: int):
        with process_request():
            form = self.db.query(Forms).filter(Forms.id == form_id).first()
            if not form:
                return {
                    "message": constants.FORM_NOT_FOUND,
                    "success": False,
                }
            return {
                "message": constants.FORM_FETCHED,
                "success": True,
                "data": form.to_dict(),
            }

    async def get_forms(self):
        with process_request():
            form = self.db.query(Forms).order_by(Forms.id).all()
            if not form:
                return {"message": constants.FORM_NOT_FOUND, "success": False}

            forms = [f.to_dict() for f in form]
            return {"message": constants.FORM_FETCHED, "success": True, "data": forms}

    async def get_forms_count(self):
        with process_request():
            form_count = self.db.query(Forms).order_by(Forms.id).count()
            if not form_count:
                return {"message": constants.FORM_NOT_FOUND, "success": True, "data": 0}
            return {
                "message": constants.FORM_FETCHED,
                "success": True,
                "data": form_count,
            }
