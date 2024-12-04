"""new db changes

Revision ID: cffbf7cd1e03
Revises: dad116d24ed2
Create Date: 2024-10-05 15:01:23.516893

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql import func


# revision identifiers, used by Alembic.
revision: str = 'cffbf7cd1e03'
down_revision: Union[str, None] = 'dad116d24ed2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create the company table
    op.create_table(
        "company",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("name", sa.String(50), nullable=True),
        sa.Column("address", sa.String(255), nullable=True),
        sa.Column("email", sa.String(50), nullable=True),
        sa.Column("admin", sa.Boolean, default=False),
        sa.Column("is_active", sa.Boolean, default=True),
        sa.Column("created_ts", sa.DateTime(timezone=True), server_default=func.now()),
        sa.Column(
            "updated_ts",
            sa.DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),
        ),
    )

    # Create the users table
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("company_id", sa.Integer, sa.ForeignKey("company.id")),
        sa.Column("first_name", sa.String(50), nullable=False),
        sa.Column("last_name", sa.String(50), nullable=False),
        sa.Column("phone", sa.String, nullable=True),
        sa.Column("image", sa.String, nullable=True),
        sa.Column("email", sa.String, unique=True, nullable=False),
        sa.Column(
            "account_type",
            sa.Enum("user", "admin", name="accounttype_enum"),
            nullable=False,
        ),
        sa.Column("password", sa.String, nullable=False),
        sa.Column("is_active", sa.Boolean, default=False),
        sa.Column("is_verified", sa.Boolean, default=False),
        sa.Column("verification_code", sa.Text, nullable=True),
        sa.Column("last_login", sa.DateTime(timezone=True), nullable=True),
        sa.Column("country_code", sa.String, nullable=True),
        sa.Column("created_ts", sa.DateTime(timezone=True), server_default=func.now()),
        sa.Column(
            "updated_ts",
            sa.DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),
        ),
    )

    # Create the user_sessions table
    op.create_table(
        "user_sessions",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id")),
        sa.Column("token", sa.Text),
        sa.Column("created_ts", sa.DateTime(timezone=True), server_default=func.now()),
        sa.Column(
            "updated_ts",
            sa.DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),
        ),
    )

    # Create the user_details table
    op.create_table(
        "user_details",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id")),
        sa.Column("gender", sa.String, nullable=True),
        sa.Column("notification", sa.Boolean, nullable=True),
        sa.Column("field_of_study", sa.String, nullable=True),
        sa.Column("fcm_token", sa.String, nullable=True),
        sa.Column("address", sa.String, nullable=True),
        sa.Column("dob", sa.Date, nullable=True),
        sa.Column("answer_count", sa.Integer, nullable=True),
        sa.Column("question_set", sa.Integer, nullable=True),
        sa.Column("profile_summary", sa.Text, nullable=True),
        sa.Column("journal_summary", sa.Text, nullable=True),
        sa.Column("quiz_summary", sa.Text, nullable=True),
        sa.Column("is_profile_questions_generated", sa.Boolean, default=False),
        sa.Column("js_lastupdated", sa.DateTime(timezone=True), nullable=True),
        sa.Column("qs_lastupdated", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ps_lastupdated", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_ts", sa.DateTime(timezone=True), server_default=func.now()),
        sa.Column(
            "updated_ts",
            sa.DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),
        ),
    )

    # Create the quizs table
    op.create_table(
        "quizs",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id")),
        sa.Column(
            "status",
            sa.Enum("pending", "completed", name="quiz_status_enum"),
            nullable=False,
        ),
        sa.Column("current_question_id", sa.Integer, nullable=True),
        sa.Column("date_completed", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_ts", sa.DateTime(timezone=True), server_default=func.now()),
        sa.Column(
            "updated_ts",
            sa.DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),
        ),
    )

    # Create the questions table
    op.create_table(
        "questions",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id")),
        sa.Column("quiz_id", sa.Integer, sa.ForeignKey("quizs.id")),
        sa.Column("details", sa.Text, nullable=True),
        sa.Column("options", sa.Text, nullable=True),
        sa.Column("correct_answer", sa.Text, nullable=True),
        sa.Column("user_answer", sa.Text, nullable=True),
        sa.Column("hint", sa.Text, nullable=True),
        sa.Column("is_answered", sa.Boolean, default=False),
        sa.Column("is_abandoned", sa.Boolean, default=False),
        sa.Column("is_answer_correct", sa.Boolean, default=False),
        sa.Column("start_datetime", sa.DateTime(timezone=True), nullable=True),
        sa.Column("end_datetime", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_ts", sa.DateTime(timezone=True), server_default=func.now()),
        sa.Column(
            "updated_ts",
            sa.DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),
        ),
    )

    # Create the journal table
    op.create_table(
        "journal",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id")),
        sa.Column("journal_details", sa.Text, nullable=False),
        sa.Column("journal_summary", sa.Text, nullable=True),
        sa.Column("is_questions_generated", sa.Boolean, nullable=True),
        sa.Column("created_ts", sa.DateTime(timezone=True), server_default=func.now()),
        sa.Column(
            "updated_ts",
            sa.DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),
        ),
    )

    # Create the prompts table
    op.create_table(
        "prompts",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("prompt_type", sa.String(25), nullable=True),
        sa.Column("prompt", sa.Text, nullable=True),
        sa.Column("created_ts", sa.DateTime(timezone=True), server_default=func.now()),
        sa.Column(
            "updated_ts",
            sa.DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),
        ),
    )

    # Create the forms table
    op.create_table(
        "forms",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("name", sa.String(50), nullable=True),
        sa.Column("is_enabled", sa.Boolean, default=True),
        sa.Column("created_ts", sa.DateTime(timezone=True), server_default=func.now()),
        sa.Column(
            "updated_ts",
            sa.DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),
        ),
    )

    # Create the form_groups table
    op.create_table(
        "form_groups",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("form_id", sa.Integer, sa.ForeignKey("forms.id")),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("slug", sa.String(50), nullable=False),
        sa.Column("is_enabled", sa.Boolean, default=True),
        sa.Column("created_ts", sa.DateTime(timezone=True), server_default=func.now()),
        sa.Column(
            "updated_ts",
            sa.DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),
        ),
    )

    # Create the form_group_fields table
    op.create_table(
        "form_group_fields",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("form_group_id", sa.Integer, sa.ForeignKey("form_groups.id")),
        sa.Column("field_type", sa.String(15), nullable=True),
        sa.Column("field_name", sa.String(50), nullable=True),
        sa.Column("options", sa.Text, nullable=True),
        sa.Column("slug", sa.String(50), nullable=False),
        sa.Column("is_enabled", sa.Boolean, default=True),
        sa.Column("is_add_more", sa.Boolean, default=False),
        sa.Column("created_ts", sa.DateTime(timezone=True), server_default=func.now()),
        sa.Column(
            "updated_ts",
            sa.DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),
        ),
    )


def downgrade() -> None:
    # Drop tables in reverse order
    pass
