"""add Language model, add field language to User model

Revision ID: 63d2f5db026d
Revises: 1008e5e21523
Create Date: 2019-12-23 21:59:14.364803

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '63d2f5db026d'
down_revision = '1008e5e21523'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('language',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('code', sa.String(length=5), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('code'),
    sa.UniqueConstraint('name')
    )
    
    with op.batch_alter_table('user') as batch_op:
        batch_op.add_column(sa.Column('language_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_user_language_id_language', 'language', ['language_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user') as batch_op:
        batch_op.drop_constraint('fk_user_language_id_language', type_='foreignkey')
        batch_op.drop_column('language_id')
    op.drop_table('language')
    # ### end Alembic commands ###
