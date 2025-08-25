"""add indexes to intraday_smart"""
from alembic import op

revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None

def upgrade():
    op.create_index(
        'idx_intraday_smart_ticker',
        'intraday_smart',
        ['ticker'],
    )
    op.create_index(
        'idx_intraday_smart_ticker_created_at',
        'intraday_smart',
        ['ticker', 'created_at'],
    )
 
def downgrade():
    op.drop_index('idx_intraday_smart_ticker', table_name='intraday_smart')
    op.drop_index('idx_intraday_smart_ticker_created_at', table_name='intraday_smart')
