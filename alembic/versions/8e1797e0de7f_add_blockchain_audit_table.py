"""add blockchain audit table

Revision ID: 8e1797e0de7f
Revises: 
Create Date: 2025-10-09 11:21:23.012520

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '8e1797e0de7f'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'blockchain_audit',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('block_hash', sa.String(length=64), nullable=False),
        sa.Column('previous_hash', sa.String(length=64), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('entity_type', sa.String(length=50), nullable=False),
        sa.Column('entity_id', sa.Integer(), nullable=False),
        sa.Column('details', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('proof', sa.Text(), nullable=False),
        sa.Column('nonce', sa.Integer(), nullable=False, server_default='0'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for better query performance
    op.create_index('ix_blockchain_audit_id', 'blockchain_audit', ['id'])
    op.create_index('ix_blockchain_audit_block_hash', 'blockchain_audit', ['block_hash'], unique=True)
    op.create_index('ix_blockchain_audit_user_id', 'blockchain_audit', ['user_id'])
    op.create_index('ix_blockchain_audit_entity', 'blockchain_audit', ['entity_type', 'entity_id'])


def downgrade() -> None:
    # Drop indexes first
    op.drop_index('ix_blockchain_audit_entity', table_name='blockchain_audit')
    op.drop_index('ix_blockchain_audit_user_id', table_name='blockchain_audit')
    op.drop_index('ix_blockchain_audit_block_hash', table_name='blockchain_audit')
    op.drop_index('ix_blockchain_audit_id', table_name='blockchain_audit')
    
    # Drop the table
    op.drop_table('blockchain_audit')
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass

