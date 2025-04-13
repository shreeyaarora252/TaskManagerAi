"""Add task priority

Revision ID: 039db099560e
Revises: d82f336db269
Create Date: 2025-04-10 00:05:17.362789

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '039db099560e'
down_revision = 'd82f336db269'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('task', schema=None) as batch_op:
        batch_op.add_column(sa.Column(
            'priority',
            sa.String(length=10),
            nullable=False,
            server_default='MEDIUM'
        ))


def downgrade():
    with op.batch_alter_table('task', schema=None) as batch_op:
        batch_op.drop_column('priority')


