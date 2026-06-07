"""e27: recursos de classe com usos (recarga por descanso)

Revision ID: b2d3f4061728
Revises: a1c2e3f40526
Create Date: 2026-06-06 21:55:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b2d3f4061728'
down_revision = 'a1c2e3f40526'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('personagens', schema=None) as batch_op:
        batch_op.add_column(sa.Column('recursos', sa.JSON(), nullable=True))


def downgrade():
    with op.batch_alter_table('personagens', schema=None) as batch_op:
        batch_op.drop_column('recursos')
