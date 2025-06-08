"""create intraday_smart table"""
from alembic import op
import sqlalchemy as sa

revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'intraday_smart',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('ticker', sa.String, nullable=False),
        sa.Column('price', sa.Float),
        sa.Column('change_val', sa.Float),
        sa.Column('change_percent', sa.Float),
        sa.Column('volume', sa.Integer),
        sa.Column('high', sa.Float),
        sa.Column('low', sa.Float),
        sa.Column('source', sa.String),
        sa.Column('timestamp', sa.String),
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
    )

def downgrade():
    op.drop_table('intraday_smart')
