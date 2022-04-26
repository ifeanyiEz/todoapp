"""empty message

Revision ID: 566acb43a9d7
Revises: 74d93721871c
Create Date: 2021-08-02 02:54:30.918270

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '566acb43a9d7'
down_revision = '74d93721871c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('todolists', sa.Column('completed', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('todolists', 'completed')
    # ### end Alembic commands ###
