"""initial

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('google_id', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('access_token', sa.Text(), nullable=False),
        sa.Column('refresh_token', sa.Text(), nullable=True),
        sa.Column('token_expiry', sa.TIMESTAMP(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('google_id')
    )

    op.create_table(
        'raw_emails',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('gmail_message_id', sa.String(), nullable=False),
        sa.Column('subject', sa.Text(), nullable=True),
        sa.Column('snippet', sa.Text(), nullable=True),
        sa.Column('received_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('processed', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('gmail_message_id')
    )

    op.create_table(
        'transactions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('raw_email_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('merchant', sa.String(), nullable=True),
        sa.Column('amount', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('currency', sa.String(length=3), nullable=True),
        sa.Column('category', sa.String(), nullable=True),
        sa.Column('date', sa.Date(), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('flagged', sa.Boolean(), nullable=True),
        sa.Column('flag_reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(['raw_email_id'], ['raw_emails.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('transactions')
    op.drop_table('raw_emails')
    op.drop_table('users')
