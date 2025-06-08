"""create trades_simules table"""
from alembic import op
import sqlalchemy as sa

revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'trades_simules',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('ticker', sa.String),
        sa.Column('prix_achat', sa.Float),
        sa.Column('quantite', sa.Integer),
        sa.Column('frais', sa.Float),
        sa.Column('montant_total', sa.Float),
        sa.Column('sl', sa.Float),
        sa.Column('tp', sa.Float),
        sa.Column('exit_price', sa.Float),
        sa.Column('date', sa.DateTime, default=sa.func.now()),
        sa.Column('provenance', sa.String),
        sa.Column('note', sa.String),
    )

def downgrade():
    op.drop_table('trades_simules')
