"""e35: classes_extras no personagem (multiclasse)

Revision ID: a7c8d9e0b154
Revises: f6b7c8d90b43
Create Date: 2026-06-07 11:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a7c8d9e0b154'
down_revision = 'f6b7c8d90b43'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('personagens', schema=None) as batch_op:
        batch_op.add_column(sa.Column('classes_extras', sa.JSON(), nullable=True))


def downgrade():
    with op.batch_alter_table('personagens', schema=None) as batch_op:
        batch_op.drop_column('classes_extras')
