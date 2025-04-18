"""Change user.id to String

Revision ID: 79bcd7b76eb0
Revises: 039db099560e
Create Date: 2025-04-12 22:36:29.196820

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '79bcd7b76eb0'
down_revision = '039db099560e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user')
    op.drop_table('subtask')
    op.drop_table('task')
    with op.batch_alter_table('tasks', schema=None) as batch_op:
        batch_op.alter_column('user_id',
               existing_type=sa.INTEGER(),
               type_=sa.String(length=100),
               existing_nullable=False)
        batch_op.alter_column('priority',
               existing_type=sa.VARCHAR(length=6),
               nullable=False)

    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('id',
               existing_type=sa.INTEGER(),
               type_=sa.String(length=100),
               existing_nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('id',
               existing_type=sa.String(length=100),
               type_=sa.INTEGER(),
               existing_nullable=False)

    with op.batch_alter_table('tasks', schema=None) as batch_op:
        batch_op.alter_column('priority',
               existing_type=sa.VARCHAR(length=6),
               nullable=True)
        batch_op.alter_column('user_id',
               existing_type=sa.String(length=100),
               type_=sa.INTEGER(),
               existing_nullable=False)

    op.create_table('task',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('title', sa.VARCHAR(length=100), nullable=False),
    sa.Column('description', sa.VARCHAR(length=200), nullable=True),
    sa.Column('completed', sa.BOOLEAN(), nullable=True),
    sa.Column('user_id', sa.INTEGER(), nullable=False),
    sa.Column('created_at', sa.DATETIME(), nullable=True),
    sa.Column('category', sa.VARCHAR(length=50), nullable=True),
    sa.Column('reminder_time', sa.DATETIME(), nullable=True),
    sa.Column('reminder_sent', sa.BOOLEAN(), nullable=True),
    sa.Column('priority', sa.VARCHAR(length=10), server_default=sa.text("'MEDIUM'"), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('subtask',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('title', sa.VARCHAR(length=100), nullable=False),
    sa.Column('completed', sa.BOOLEAN(), nullable=True),
    sa.Column('task_id', sa.INTEGER(), nullable=False),
    sa.Column('created_at', sa.DATETIME(), nullable=True),
    sa.ForeignKeyConstraint(['task_id'], ['task.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('username', sa.VARCHAR(length=80), nullable=False),
    sa.Column('password', sa.VARCHAR(length=120), nullable=False),
    sa.Column('push_token', sa.VARCHAR(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('username')
    )
    # ### end Alembic commands ###
