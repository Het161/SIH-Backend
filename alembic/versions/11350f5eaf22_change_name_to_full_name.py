"""change_name_to_full_name

Revision ID: 11350f5eaf22
Revises: 8e1797e0de7f
Create Date: 2025-10-28 14:28:22.696434

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '11350f5eaf22'
down_revision: Union[str, Sequence[str], None] = '8e1797e0de7f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Rename column from 'name' to 'full_name'
    op.alter_column('users', 'name', new_column_name='full_name')

def downgrade():
    # Rename column back from 'full_name' to 'name'
    op.alter_column('users', 'full_name', new_column_name='name')
