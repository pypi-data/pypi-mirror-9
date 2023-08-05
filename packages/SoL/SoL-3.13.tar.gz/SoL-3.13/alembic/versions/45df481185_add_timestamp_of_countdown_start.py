# :Progetto:  SoL -- Add timestamp of countdown start
# :Creato:    2014-08-30 17:26:10.109394
# :Autore:    Lele Gaifax <lele@metapensiero.it>
# :Licenza:   GNU General Public License version 3 or later
#

from alembic import op
import sqlalchemy as sa


revision = '45df481185'
down_revision = 'c2943b13a3'


def upgrade():
    op.add_column('tourneys', sa.Column('countdownstarted', sa.Integer(), nullable=True))


def downgrade():
    op.drop_column('tourneys', 'countdownstarted')
