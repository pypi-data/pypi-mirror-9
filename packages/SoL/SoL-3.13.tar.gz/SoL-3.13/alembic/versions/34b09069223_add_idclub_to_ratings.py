# :Progetto:  SoL -- Add idclub to ratings
# :Creato:    2014-11-05 12:20:57.049746
# :Autore:    Lele Gaifax <lele@metapensiero.it>
# :Licenza:   GNU General Public License version 3 or later
#

from alembic import op
import sqlalchemy as sa


revision = '34b09069223'
down_revision = '4eece1d83ff'


def upgrade():
    op.add_column('ratings', sa.Column('idclub', sa.Integer()))


def downgrade():
    op.drop_column('ratings', 'idclub')
