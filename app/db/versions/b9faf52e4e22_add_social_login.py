"""Add Social Login

Revision ID: b9faf52e4e22
Revises: 984b818f82b1
Create Date: 2026-07-05 12:11:59.888940

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'b9faf52e4e22'
down_revision: Union[str, Sequence[str], None] = '984b818f82b1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    login_type = sa.Enum(
        "EMAIL",
        "GOOGLE",
        "GITHUB",
        "FACEBOOK",
        name="login_type_enum",
    )

    login_type.create(op.get_bind(), checkfirst=True)

    op.add_column(
        "users",
        sa.Column(
            "login_type",
            login_type,
            nullable=False,
            server_default="EMAIL",
        ),
    )

    op.add_column(
        "users",
        sa.Column("social_id", sa.String(), nullable=True),
    )

    op.alter_column(
        "users",
        "password",
        existing_type=sa.String(),
        nullable=True,
    )

    op.alter_column(
        "users",
        "login_type",
        server_default=None,
    )
    # ### end Alembic commands ###


def downgrade():
    op.alter_column(
        "users",
        "password",
        existing_type=sa.String(),
        nullable=False,
    )

    op.drop_column("users", "social_id")
    op.drop_column("users", "login_type")

    sa.Enum(name="login_type_enum").drop(op.get_bind(), checkfirst=True)
    # ### end Alembic commands ###
