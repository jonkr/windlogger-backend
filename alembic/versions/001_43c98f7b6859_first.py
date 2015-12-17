"""first

Revision ID: 43c98f7b6859
Revises: 
Create Date: 2015-06-09 13:33:04.520428

"""

# revision identifiers, used by Alembic.
revision = '43c98f7b6859'
down_revision = None
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('sensors',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('type', sa.Integer(), nullable=False),
    sa.Column('latitude', sa.Float(), nullable=False),
    sa.Column('longitude', sa.Float(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('samples',
    sa.Column('sensor_id', sa.Integer(), nullable=False),
    sa.Column('date_created', sa.DateTime(), nullable=False),
    sa.Column('date_reported', sa.DateTime(), nullable=False),
    sa.Column('type', sa.Integer(), nullable=False),
    sa.Column('_data', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['sensor_id'], ['sensors.id'], ),
    sa.PrimaryKeyConstraint('sensor_id', 'date_reported', 'type')
    )
    op.create_index(op.f('ix_samples_date_created'), 'samples', ['date_created'], unique=False)
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_samples_date_created'), table_name='samples')
    op.drop_table('samples')
    op.drop_table('sensors')
    ### end Alembic commands ###
