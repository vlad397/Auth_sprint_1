"""empty message

Revision ID: ae114bd3e9db
Revises: dd7ccfb3b712
Create Date: 2022-05-25 22:47:37.385982

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'ae114bd3e9db'
down_revision = 'dd7ccfb3b712'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('auth_history', 'browser',
               existing_type=sa.TEXT(),
               nullable=True)
    op.alter_column('auth_history', 'platform',
               existing_type=sa.TEXT(),
               nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('auth_history', 'platform',
               existing_type=sa.TEXT(),
               nullable=False)
    op.alter_column('auth_history', 'browser',
               existing_type=sa.TEXT(),
               nullable=False)
    # ### end Alembic commands ###
