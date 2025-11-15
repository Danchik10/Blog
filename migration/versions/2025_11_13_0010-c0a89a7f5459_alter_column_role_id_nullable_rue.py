"""alter column role_id nullable=rue

Revision ID: c0a89a7f5459
Revises: f67c04429d4d
Create Date: 2025-11-13 00:10:50.582399

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c0a89a7f5459'
down_revision: Union[str, Sequence[str], None] = 'f67c04429d4d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Для SQLite используем batch mode
    with op.batch_alter_table('users') as batch_op:
        batch_op.alter_column('role_id', nullable=True)

def downgrade():
    with op.batch_alter_table('users') as batch_op:
        batch_op.alter_column('role_id', nullable=False)
