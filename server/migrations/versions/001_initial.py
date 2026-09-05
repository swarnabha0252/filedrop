"""Initial migration

Revision ID: 001
Revises: 
Create Date: 2026-09-05 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg


revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'files',
        sa.Column('id', pg.UUID(as_uuid=True), primary_key=True),
        sa.Column('token', sa.String(64), unique=True, nullable=False, index=True),
        sa.Column('filename', sa.String(255), nullable=False),
        sa.Column('mime_type', sa.String(128), nullable=False),
        sa.Column('size', sa.Integer(), nullable=False),
        sa.Column('storage_key', sa.String(512), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('download_count', sa.Integer(), default=0, nullable=False),
        sa.Column('download_limit', sa.Integer(), nullable=True),
        sa.Column('password_hash', sa.String(255), nullable=True),
        sa.Column('delete_token_hash', sa.String(255), nullable=False),
        sa.Column('status', sa.Enum('active', 'expired', 'deleted', name='filestatus'), default='active', nullable=False),
        sa.Index('ix_files_expires_at', 'expires_at'),
        sa.Index('ix_files_status', 'status'),
    )


def downgrade() -> None:
    op.drop_index('ix_files_status', table_name='files')
    op.drop_index('ix_files_expires_at', table_name='files')
    op.drop_table('files')
    op.execute('DROP TYPE IF EXISTS filestatus')