"""adding type to Physical quantities

Revision ID: b45b82e5c5c2
Revises: fc86c413fae5
Create Date: 2025-06-27 11:13:59.644793

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = 'b45b82e5c5c2'
down_revision = 'fc86c413fae5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('physicalquantity', 'type',
               existing_type=sa.VARCHAR(),
               nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('physicalquantity', 'type',
               existing_type=sa.VARCHAR(),
               nullable=False)
    # ### end Alembic commands ###