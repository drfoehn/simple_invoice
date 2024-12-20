"""Add discount column to invoice

Revision ID: 65906ba811da
Revises: 
Create Date: 2024-10-31 11:03:57.021519

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '65906ba811da'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('client', schema=None) as batch_op:
        batch_op.alter_column('payment_terms',
               existing_type=sa.VARCHAR(length=100),
               type_=sa.String(length=300),
               existing_nullable=True)

    with op.batch_alter_table('invoice', schema=None) as batch_op:
        batch_op.add_column(sa.Column('discount', sa.Float(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('invoice', schema=None) as batch_op:
        batch_op.drop_column('discount')

    with op.batch_alter_table('client', schema=None) as batch_op:
        batch_op.alter_column('payment_terms',
               existing_type=sa.String(length=300),
               type_=sa.VARCHAR(length=100),
               existing_nullable=True)

    # ### end Alembic commands ###
