"""wipe bad data

Revision ID: a9d60cd9728
Revises: 251118be576a
Create Date: 2015-06-12 21:27:27.806156

"""

# revision identifiers, used by Alembic.
import datetime

revision = 'a9d60cd9728'
down_revision = '251118be576a'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from sqlalchemy import DateTime

sample = table('samples', column('date_created', DateTime))

def upgrade():
    dt = datetime.datetime.utcnow() - datetime.timedelta(hours=1)
    op.execute(sample.delete().where(sample.c.date_created>=dt))


def downgrade():
    pass
