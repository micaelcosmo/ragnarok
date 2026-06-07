"""e33: moedas por tipo no personagem

Revision ID: e5a6c7d80a32
Revises: d4f5b6c70921
Create Date: 2026-06-07 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e5a6c7d80a32'
down_revision = 'd4f5b6c70921'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('personagens', schema=None) as batch_op:
        batch_op.add_column(sa.Column('moedas', sa.JSON(), nullable=True))


def downgrade():
    with op.batch_alter_table('personagens', schema=None) as batch_op:
        batch_op.drop_column('moedas')
