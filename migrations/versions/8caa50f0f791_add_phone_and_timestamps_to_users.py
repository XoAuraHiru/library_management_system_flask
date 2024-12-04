"""add_phone_and_timestamps_to_users

Revision ID: 8caa50f0f791
Revises: 
Create Date: 2024-12-05 03:38:46.574698

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime


# revision identifiers, used by Alembic.
revision = '8caa50f0f791'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Add phone column
    op.add_column('users', sa.Column('phone', sa.String(20), nullable=True))
    
    # Add timestamp columns if they don't exist
    # First check if the columns exist to avoid errors
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('users')]
    
    if 'created_at' not in columns:
        op.add_column('users', 
            sa.Column('created_at', sa.DateTime, nullable=False, 
                      server_default=sa.text('CURRENT_TIMESTAMP')))
    
    if 'updated_at' not in columns:
        op.add_column('users', 
            sa.Column('updated_at', sa.DateTime, nullable=False,
                      server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')))

def downgrade():
    # Remove added columns
    op.drop_column('users', 'phone')
    op.drop_column('users', 'created_at')
    op.drop_column('users', 'updated_at')