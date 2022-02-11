"""create proposals table/home/user/PycharmProjects/p2p_exchange/utils/migrations/versions

Revision ID: 5d1f892fc20d
Revises: c95f674f054b
Create Date: 2022-01-11 14:38:50.887263

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '5d1f892fc20d'
down_revision = 'c95f674f054b'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('token',
                    sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
                    sa.Column('token_type', sa.String, nullable=False)
                    )
    op.create_table('proposal',
                    sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
                    sa.Column('token_type', sa.Integer, sa.ForeignKey('token.id'), nullable=False),
                    sa.Column('price', sa.Float, nullable=False),
                    sa.Column('min_amount', sa.Float, nullable=False),
                    sa.Column('max_amount', sa.Float, nullable=False),
                    sa.Column('currency', sa.String, nullable=False),
                    sa.Column('proposal_type', sa.String, nullable=False),
                    sa.Column('payment_method', sa.String, nullable=False),
                    sa.Column('info', sa.String, nullable=False),
                    sa.Column('user_id', sa.Integer, sa.ForeignKey('user.id')))


def downgrade():
    op.drop_table('proposal')
    op.drop_table('token')
