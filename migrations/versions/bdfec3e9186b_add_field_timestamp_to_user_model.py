"""add field timestamp to User model

Revision ID: bdfec3e9186b
Revises: e14e56a29cb1
Create Date: 2019-12-25 19:44:34.328291

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bdfec3e9186b'
down_revision = 'e14e56a29cb1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('timestamp', sa.DateTime(), nullable=True))
    op.create_index(op.f('ix_user_timestamp'), 'user', ['timestamp'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_user_timestamp'), table_name='user')
    op.drop_column('user', 'timestamp')
    # ### end Alembic commands ###