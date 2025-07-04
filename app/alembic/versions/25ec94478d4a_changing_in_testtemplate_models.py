"""Changing in  testtemplate models

Revision ID: 25ec94478d4a
Revises: 3f68dc9b9b4d
Create Date: 2025-06-27 18:52:10.746056

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = '25ec94478d4a'
down_revision = '3f68dc9b9b4d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('testtemplate', 'updatedBy',
               existing_type=sa.UUID(),
               nullable=True)
    op.drop_column('testtemplate', 'createdBy')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('testtemplate', sa.Column('createdBy', sa.UUID(), autoincrement=False, nullable=False))
    op.alter_column('testtemplate', 'updatedBy',
               existing_type=sa.UUID(),
               nullable=False)
    # ### end Alembic commands ###