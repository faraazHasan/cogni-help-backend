"""add new column in form_groups table

Revision ID: 202011e066b2
Revises: cffbf7cd1e03
Create Date: 2024-10-09 15:06:48.022106

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '202011e066b2'
down_revision: Union[str, None] = 'cffbf7cd1e03'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("form_groups",sa.Column('is_add_more', sa.BOOLEAN(), nullable=False))
    op.add_column("form_group_fields",sa.Column('is_add_more', sa.BOOLEAN(), nullable=False))


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.INTEGER(), server_default=sa.text("nextval('users_id_seq'::regclass)"), autoincrement=True, nullable=False),
    sa.Column('company_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('first_name', sa.VARCHAR(length=50), autoincrement=False, nullable=False),
    sa.Column('last_name', sa.VARCHAR(length=50), autoincrement=False, nullable=False),
    sa.Column('phone', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('image', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('email', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('account_type', postgresql.ENUM('user', 'admin', name='accounttype_enum'), autoincrement=False, nullable=False),
    sa.Column('password', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('is_active', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.Column('is_verified', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.Column('verification_code', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('last_login', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
    sa.Column('country_code', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('created_ts', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), autoincrement=False, nullable=True),
    sa.Column('updated_ts', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['company_id'], ['company.id'], name='users_company_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='users_pkey'),
    sa.UniqueConstraint('email', name='users_email_key'),
    postgresql_ignore_search_path=False
    )
    op.create_index('ix_users_id', 'users', ['id'], unique=False)
    op.create_table('user_sessions',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('token', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('created_ts', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), autoincrement=False, nullable=True),
    sa.Column('updated_ts', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='user_sessions_user_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='user_sessions_pkey')
    )
    op.create_index('ix_user_sessions_id', 'user_sessions', ['id'], unique=False)
    op.create_table('user_details',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('gender', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('notification', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.Column('field_of_study', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('fcm_token', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('address', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('dob', sa.DATE(), autoincrement=False, nullable=True),
    sa.Column('answer_count', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('question_set', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('profile_summary', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('journal_summary', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('quiz_summary', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('is_profile_questions_generated', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.Column('js_lastupdated', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
    sa.Column('qs_lastupdated', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
    sa.Column('ps_lastupdated', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
    sa.Column('created_ts', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), autoincrement=False, nullable=True),
    sa.Column('updated_ts', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='user_details_user_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='user_details_pkey')
    )
    op.create_index('ix_user_details_id', 'user_details', ['id'], unique=False)
    op.create_table('company',
    sa.Column('id', sa.INTEGER(), server_default=sa.text("nextval('company_id_seq'::regclass)"), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(length=50), autoincrement=False, nullable=True),
    sa.Column('address', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.Column('email', sa.VARCHAR(length=50), autoincrement=False, nullable=True),
    sa.Column('admin', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.Column('is_active', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.Column('created_ts', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), autoincrement=False, nullable=True),
    sa.Column('updated_ts', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='company_pkey'),
    postgresql_ignore_search_path=False
    )
    op.create_index('ix_company_id', 'company', ['id'], unique=False)
    op.create_table('form_group_fields',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('form_group_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('field_type', sa.VARCHAR(length=15), autoincrement=False, nullable=True),
    sa.Column('field_name', sa.VARCHAR(length=50), autoincrement=False, nullable=True),
    sa.Column('options', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('slug', sa.VARCHAR(length=50), autoincrement=False, nullable=False),
    sa.Column('is_enabled', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.Column('is_add_more', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.Column('created_ts', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), autoincrement=False, nullable=True),
    sa.Column('updated_ts', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['form_group_id'], ['form_groups.id'], name='form_group_fields_form_group_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='form_group_fields_pkey')
    )
    op.create_index('ix_form_group_fields_id', 'form_group_fields', ['id'], unique=False)
    op.create_table('questions',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('quiz_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('details', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('options', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('correct_answer', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('user_answer', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('hint', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('is_answered', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.Column('is_abandoned', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.Column('is_answer_correct', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.Column('start_datetime', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
    sa.Column('end_datetime', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
    sa.Column('created_ts', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), autoincrement=False, nullable=True),
    sa.Column('updated_ts', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['quiz_id'], ['quizs.id'], name='questions_quiz_id_fkey'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='questions_user_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='questions_pkey')
    )
    op.create_index('ix_questions_id', 'questions', ['id'], unique=False)
    op.create_table('prompts',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('prompt_type', sa.VARCHAR(length=25), autoincrement=False, nullable=True),
    sa.Column('prompt', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('created_ts', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), autoincrement=False, nullable=True),
    sa.Column('updated_ts', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='prompts_pkey')
    )
    op.create_index('ix_prompts_id', 'prompts', ['id'], unique=False)
    op.create_table('forms',
    sa.Column('id', sa.INTEGER(), server_default=sa.text("nextval('forms_id_seq'::regclass)"), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(length=50), autoincrement=False, nullable=True),
    sa.Column('is_enabled', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.Column('created_ts', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), autoincrement=False, nullable=True),
    sa.Column('updated_ts', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='forms_pkey'),
    postgresql_ignore_search_path=False
    )
    op.create_index('ix_forms_id', 'forms', ['id'], unique=False)
    op.create_table('form_groups',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('form_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('slug', sa.VARCHAR(length=50), autoincrement=False, nullable=False),
    sa.Column('is_enabled', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.Column('created_ts', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), autoincrement=False, nullable=True),
    sa.Column('updated_ts', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['form_id'], ['forms.id'], name='form_groups_form_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='form_groups_pkey')
    )
    op.create_index('ix_form_groups_id', 'form_groups', ['id'], unique=False)
    op.create_table('journal',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('journal_details', sa.TEXT(), autoincrement=False, nullable=False),
    sa.Column('journal_summary', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('is_questions_generated', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.Column('created_ts', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), autoincrement=False, nullable=True),
    sa.Column('updated_ts', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='journal_user_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='journal_pkey')
    )
    op.create_index('ix_journal_id', 'journal', ['id'], unique=False)
    op.create_table('quizs',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('status', postgresql.ENUM('pending', 'completed', name='quiz_status_enum'), autoincrement=False, nullable=False),
    sa.Column('current_question_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('date_completed', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
    sa.Column('created_ts', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), autoincrement=False, nullable=True),
    sa.Column('updated_ts', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='quizs_user_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='quizs_pkey')
    )
    op.create_index('ix_quizs_id', 'quizs', ['id'], unique=False)
    # ### end Alembic commands ###
