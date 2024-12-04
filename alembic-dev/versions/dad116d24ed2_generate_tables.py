"""generate tables

Revision ID: dad116d24ed2
Revises: 
Create Date: 2024-09-04 16:54:02.696122

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    Text,
    DateTime,
    Date,
    ForeignKey,
    Enum as sqEnum,
)
from datetime import datetime

# revision identifiers, used by Alembic.
revision: str = 'dad116d24ed2'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Creating the "users" table
    op.create_table(
        "users",
        Column("id", Integer, primary_key=True, index=True),
        Column("full_name", String),
        Column("phone", String, nullable=True),
        Column("image", String, nullable=True),
        Column("email", String, unique=True),
        sa.Column(
            "account_type",
            sa.Enum("user", "admin", name="account_enum"),
            nullable=False,
        ),
        Column("password", String),
        Column("is_active", Boolean, default=False),
        Column("is_verified", Boolean, default=False),
        Column("verification_code", Text, nullable=True),
        Column("last_login", DateTime(timezone=True), nullable=True),
        Column("country_code", String, nullable=True),
        Column("created_ts", DateTime(timezone=True), default=datetime.now),
        Column(
            "updated_ts",
            DateTime(timezone=True),
            default=datetime.now,
            onupdate=datetime.now,
        ),
    )

    # Creating the "user_sessions" table
    op.create_table(
        "user_sessions",
        Column("id", Integer, primary_key=True, index=True),
        Column("user_id", Integer, ForeignKey("users.id")),
        Column("token", Text),
        Column("created_ts", DateTime(timezone=True), default=datetime.now),
        Column(
            "updated_ts",
            DateTime(timezone=True),
            default=datetime.now,
            onupdate=datetime.now,
        ),
    )

    # Creating the "questions" table
    op.create_table(
        "questions",
        Column("id", Integer, primary_key=True, index=True),
        Column("user_id", Integer, ForeignKey("users.id")),
        Column("question", Text, nullable=True),
        Column("hint", Text, nullable=True),
        Column("is_answered", Boolean, default=False),
        Column("source", String, nullable=False),
        Column("created_ts", DateTime(timezone=True), default=datetime.now),
        Column(
            "updated_ts",
            DateTime(timezone=True),
            default=datetime.now,
            onupdate=datetime.now,
        ),
    )

    # Creating the "general_questions" table
    op.create_table(
        "general_questions",
        Column("id", Integer, primary_key=True, index=True),
        Column("questions", Text),
        Column("created_ts", DateTime(timezone=True), default=datetime.now),
        Column(
            "updated_ts",
            DateTime(timezone=True),
            default=datetime.now,
            onupdate=datetime.now,
        ),
    )

    # Creating the "work_histories" table
    op.create_table(
        "work_histories",
        Column("id", Integer, primary_key=True, index=True),
        Column("user_id", Integer, ForeignKey("users.id")),
        Column("company_name", String, nullable=True),
        Column("designation", String, nullable=True),
        Column("start_date", DateTime(timezone=True), nullable=True),
        Column("end_date", DateTime(timezone=True), nullable=True),
        Column("still_working_here", Boolean, nullable=True),
        Column("created_ts", DateTime(timezone=True), default=datetime.now),
        Column(
            "updated_ts",
            DateTime(timezone=True),
            default=datetime.now,
            onupdate=datetime.now,
        ),
    )

    # Creating the "user_details" table
    op.create_table(
        "user_details",
        Column("id", Integer, primary_key=True, index=True),
        Column("user_id", Integer, ForeignKey("users.id")),
        Column("gender", String, nullable=True),
        Column("notification", Boolean, nullable=True),
        Column("field_of_study", String, nullable=True),
        Column("fcm_token", String, nullable=True),
        Column("address", String, nullable=True),
        Column("dob", Date, nullable=True),
        Column("answer_count", Integer, nullable=True),
        Column("question_set", Integer, nullable=True),
        Column("is_profile_questions_generated", Boolean, default=False),
        Column("created_ts", DateTime(timezone=True), default=datetime.now),
        Column(
            "updated_ts",
            DateTime(timezone=True),
            default=datetime.now,
            onupdate=datetime.now,
        ),
    )

    # Creating the "answers_options" table
    op.create_table(
        "answers_options",
        Column("id", Integer, primary_key=True, index=True),
        Column("question_id", Integer, ForeignKey("questions.id")),
        Column("option", Text, nullable=True),
        Column("is_correct", Boolean, default=False),
        Column("created_ts", DateTime(timezone=True), default=datetime.now),
        Column(
            "updated_ts",
            DateTime(timezone=True),
            default=datetime.now,
            onupdate=datetime.now,
        ),
    )

    # Creating the "educations" table
    op.create_table(
        "educations",
        Column("id", Integer, primary_key=True, index=True),
        Column("user_id", Integer, ForeignKey("users.id")),
        Column("field_of_study", String, nullable=True),
        Column("level_of_education", String, nullable=True),
        Column("start_date", DateTime(timezone=True), nullable=True),
        Column("end_date", DateTime(timezone=True), nullable=True),
        Column("appearing", Boolean, nullable=True),
        Column("created_ts", DateTime(timezone=True), default=datetime.now),
        Column(
            "updated_ts",
            DateTime(timezone=True),
            default=datetime.now,
            onupdate=datetime.now,
        ),
    )

    # Creating the "personal_preferences" table
    op.create_table(
        "personal_preferences",
        Column("id", Integer, primary_key=True, index=True),
        Column("user_id", Integer, ForeignKey("users.id")),
        Column("favourite_foods", Text, nullable=True),
        Column("favourite_places", Text, nullable=True),
        Column("favourite_movies", Text, nullable=True),
        Column("favourite_music", Text, nullable=True),
        Column("favourite_books", Text, nullable=True),
        Column("hobbies_and_interests", Text, nullable=True),
        Column("special_notes", Text, nullable=True),
        Column("created_ts", DateTime(timezone=True), default=datetime.now),
        Column(
            "updated_ts",
            DateTime(timezone=True),
            default=datetime.now,
            onupdate=datetime.now,
        ),
    )

    # Creating the "journal" table
    op.create_table(
        "journal",
        Column("id", Integer, primary_key=True, index=True),
        Column("user_id", Integer, ForeignKey("users.id")),
        Column("summary", Text),
        Column("gpt_summary", Text),
        Column("is_questions_generated", Boolean, nullable=True),
        Column("created_ts", DateTime(timezone=True), default=datetime.now),
        Column(
            "updated_ts",
            DateTime(timezone=True),
            default=datetime.now,
            onupdate=datetime.now,
        ),
    )

    # Creating the "family_details" table
    op.create_table(
        "family_details",
        Column("id", Integer, primary_key=True, index=True),
        Column("user_id", Integer, ForeignKey("users.id")),
        Column("relationship", String, nullable=True),
        Column("name", String, nullable=True),
        Column("age", Integer, nullable=True),
        Column("occupation", String, nullable=True),
        Column("email", String, nullable=True),
        Column("special_notes", String, nullable=True),
        Column("created_ts", DateTime(timezone=True), default=datetime.now),
        Column(
            "updated_ts",
            DateTime(timezone=True),
            default=datetime.now,
            onupdate=datetime.now,
        ),
    )


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
