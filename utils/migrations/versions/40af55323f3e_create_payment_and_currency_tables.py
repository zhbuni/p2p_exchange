"""create_payment_and_currency_tables

Revision ID: 40af55323f3e
Revises: 5d1f892fc20d
Create Date: 2022-02-11 15:06:29.669454

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '40af55323f3e'
down_revision = '5d1f892fc20d'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_table('payment')
    op.create_table('currency',
                    sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
                    sa.Column('type', sa.String, nullable=False)
                    )
    op.create_table('payment',
                    sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
                    sa.Column('russian_title', sa.String, nullable=False),
                    sa.Column('english_title', sa.String, nullable=False),
                    )


def downgrade():
    op.drop_table('currency')
    op.drop_table('payment')
