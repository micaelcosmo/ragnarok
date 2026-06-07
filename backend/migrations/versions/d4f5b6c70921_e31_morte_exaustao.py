"""e31: testes contra a morte + exaustão no personagem

Revision ID: d4f5b6c70921
Revises: c3e4a5b60810
Create Date: 2026-06-07 09:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd4f5b6c70921'
down_revision = 'c3e4a5b60810'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('personagens', schema=None) as batch_op:
        batch_op.add_column(sa.Column('mortes_sucesso', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('mortes_falha', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('exaustao', sa.Integer(), nullable=True))


def downgrade():
    with op.batch_alter_table('personagens', schema=None) as batch_op:
        batch_op.drop_column('exaustao')
        batch_op.drop_column('mortes_falha')
        batch_op.drop_column('mortes_sucesso')
