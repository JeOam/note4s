"""add anchor to notification model

Revision ID: 869c856002ba
Revises: 047ee36cae07
Create Date: 2016-12-22 14:36:44.236214

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '869c856002ba'
down_revision = '047ee36cae07'
branch_labels = None
depends_on = None

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('notification', sa.Column('anchor', postgresql.UUID(as_uuid=True), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('notification', 'anchor')
    ### end Alembic commands ###
