"""empty message

Revision ID: a7df4de4f167
Revises: 
Create Date: 2022-04-28 20:41:32.143268

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a7df4de4f167'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user_account', sa.Column('occupation', sa.String(length=50), nullable=True))
    op.add_column('user_account', sa.Column('bio', sa.String(length=500), nullable=True))
    op.add_column('user_account', sa.Column('website', sa.String(length=120), nullable=True))
    op.add_column('user_account', sa.Column('comment_ids', sa.String(length=120), nullable=True))
    op.add_column('user_account', sa.Column('interests', sa.String(length=120), nullable=True))
    op.add_column('user_account', sa.Column('friend_ids', sa.String(length=120), nullable=True))
    op.add_column('user_account', sa.Column('privacy_setting', sa.String(length=120), nullable=True))
    op.add_column('user_account', sa.Column('organization_name', sa.String(length=120), nullable=True))
    op.add_column('user_account', sa.Column('years_in_business', sa.String(length=2), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user_account', 'years_in_business')
    op.drop_column('user_account', 'organization_name')
    op.drop_column('user_account', 'privacy_setting')
    op.drop_column('user_account', 'friend_ids')
    op.drop_column('user_account', 'interests')
    op.drop_column('user_account', 'comment_ids')
    op.drop_column('user_account', 'website')
    op.drop_column('user_account', 'bio')
    op.drop_column('user_account', 'occupation')
    # ### end Alembic commands ###
