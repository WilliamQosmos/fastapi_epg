"""Add table coincindence

Revision ID: 86c2d6443453
Revises: 21efa4a57e71
Create Date: 2024-11-05 16:47:06.972296

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '86c2d6443453'
down_revision = '21efa4a57e71'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('coincidences',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('first_user_id', sa.Integer(), nullable=False),
    sa.Column('second_user_id', sa.Integer(), nullable=False),
    sa.Column('compared', sa.Boolean(), server_default='false', nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk__coincidences'))
    )
    op.create_index(op.f('ix__coincidences_id'), 'coincidences', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix__coincidences_id'), table_name='coincidences')
    op.drop_table('coincidences')
    # ### end Alembic commands ###
