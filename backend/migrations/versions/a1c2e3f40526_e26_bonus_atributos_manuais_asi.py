"""e26: bonus_atributos_manuais no personagem (pool de ASI reversível)

Revision ID: a1c2e3f40526
Revises: 7ed254ff640a
Create Date: 2026-06-06 21:20:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1c2e3f40526'
down_revision = '7ed254ff640a'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('personagens', schema=None) as batch_op:
        batch_op.add_column(sa.Column('bonus_atributos_manuais', sa.JSON(), nullable=True))


def downgrade():
    with op.batch_alter_table('personagens', schema=None) as batch_op:
        batch_op.drop_column('bonus_atributos_manuais')
