"""alter table user: add column role_id

Revision ID: f67c04429d4d
Revises: db1c72bb32ca
Create Date: 2025-11-13 00:02:36.871727

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f67c04429d4d'
down_revision: Union[str, Sequence[str], None] = 'db1c72bb32ca'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Для SQLite используем batch mode
    with op.batch_alter_table('users') as batch_op:
        batch_op.add_column(sa.Column('role_id', sa.Integer(), nullable=False))
        batch_op.create_foreign_key(
            'fk_users_role_id',
            'roles',
            ['role_id'],
            ['id'],
            ondelete='CASCADE'
        )

def downgrade():
    with op.batch_alter_table('users') as batch_op:
        batch_op.drop_constraint('fk_users_role_id', type_='foreignkey')
        batch_op.drop_column('role_id')
