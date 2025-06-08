"""create watchlist table"""
from alembic import op
import sqlalchemy as sa

revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'watchlist',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('ticker', sa.String, unique=True, nullable=False),
        sa.Column('last_price', sa.Float),
        sa.Column('volume', sa.Integer),
        sa.Column('float', sa.Integer),
        sa.Column('change_percent', sa.Float),
        sa.Column('score', sa.Float),
        sa.Column('source', sa.String),
        sa.Column('date', sa.String),
        sa.Column('description', sa.String),
        sa.Column('updated_at', sa.DateTime),
    )

def downgrade():
    op.drop_table('watchlist')
