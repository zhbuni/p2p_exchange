"""create user table

Revision ID: c95f674f054b
Revises: 
Create Date: 2022-01-09 19:45:55.123894

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c95f674f054b'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('user',
                    sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
                    sa.Column('name', sa.String),
                    sa.Column('surname', sa.String),
                    sa.Column('telegram_id', sa.Integer))


def downgrade():
    op.drop_table('user')
