"""empty message

Revision ID: 3dd8a8208d2
Revises: 4159a3ee034
Create Date: 2015-07-20 16:02:54.293886

"""

# revision identifiers, used by Alembic.
revision = '3dd8a8208d2'
down_revision = '4159a3ee034'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('news', sa.Column('comments_count', sa.Integer(), nullable=True))
    op.add_column('news', sa.Column('comments_likes', sa.Integer(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('news', 'comments_likes')
    op.drop_column('news', 'comments_count')
    ### end Alembic commands ###
