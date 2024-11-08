"""initial

Revision ID: 21efa4a57e71
Revises:
Create Date: 2024-11-05 11:58:00.507441

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "21efa4a57e71"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("email", sa.String(length=100), nullable=False),
        sa.Column("password", sa.String(), nullable=False),
        sa.Column("first_name", sa.String(), nullable=False),
        sa.Column("last_name", sa.String(), nullable=False),
        sa.Column("gender", sa.String(), nullable=True),
        sa.Column("avatar", sa.String(), nullable=True),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk__users")),
    )
    op.create_index(op.f("ix__users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix__users_id"), "users", ["id"], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix__users_id"), table_name="users")
    op.drop_index(op.f("ix__users_email"), table_name="users")
    op.drop_table("users")
    # ### end Alembic commands ###
