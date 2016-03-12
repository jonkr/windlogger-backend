"""empty message

Revision ID: 871cea29d88a
Revises: 7d4b9c491028
Create Date: 2016-03-12 21:15:49.864020

"""

# revision identifiers, used by Alembic.
revision = '871cea29d88a'
down_revision = '7d4b9c491028'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('sensors', 'service_id')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('sensors', sa.Column('service_id', sa.VARCHAR(), autoincrement=False, nullable=True))
    ### end Alembic commands ###
