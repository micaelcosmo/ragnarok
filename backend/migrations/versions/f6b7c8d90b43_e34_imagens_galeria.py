"""e34: galeria de imagens do personagem

Revision ID: f6b7c8d90b43
Revises: e5a6c7d80a32
Create Date: 2026-06-07 10:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f6b7c8d90b43'
down_revision = 'e5a6c7d80a32'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('personagens', schema=None) as batch_op:
        batch_op.add_column(sa.Column('imagens', sa.JSON(), nullable=True))


def downgrade():
    with op.batch_alter_table('personagens', schema=None) as batch_op:
        batch_op.drop_column('imagens')
