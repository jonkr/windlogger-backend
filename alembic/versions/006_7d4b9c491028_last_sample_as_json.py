"""last_sample as json

Revision ID: 7d4b9c491028
Revises: 189dabebe500
Create Date: 2016-03-07 12:37:36.482791

"""

# revision identifiers, used by Alembic.
revision = '7d4b9c491028'
down_revision = '189dabebe500'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('sensors', sa.Column('_last_samples', sa.String(), nullable=True))
    op.drop_column('sensors', 'last_samples')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('sensors', sa.Column('last_samples', postgresql.BYTEA(), autoincrement=False, nullable=True))
    op.drop_column('sensors', '_last_samples')
    ### end Alembic commands ###
