"""e29: subraca_slug no personagem (sub-raça aplica efeitos)

Revision ID: c3e4a5b60810
Revises: b2d3f4061728
Create Date: 2026-06-07 09:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c3e4a5b60810'
down_revision = 'b2d3f4061728'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('personagens', schema=None) as batch_op:
        batch_op.add_column(sa.Column('subraca_slug', sa.String(length=60), nullable=True))


def downgrade():
    with op.batch_alter_table('personagens', schema=None) as batch_op:
        batch_op.drop_column('subraca_slug')
