# :Progetto:  SoL -- Add idowner field to top level entities
# :Creato:    2014-07-04 12:56:26.555473
# :Autore:    Lele Gaifax <lele@metapensiero.it>
# :Licenza:   GNU General Public License version 3 or later
#

from alembic import op
import sqlalchemy as sa


revision = 'c2943b13a3'
down_revision = '26651827d0f'


def upgrade():
    op.add_column('championships', sa.Column('idowner', sa.Integer(), nullable=True))
    op.add_column('clubs', sa.Column('idowner', sa.Integer(), nullable=True))
    op.add_column('players', sa.Column('idowner', sa.Integer(), nullable=True))
    op.add_column('ratings', sa.Column('idowner', sa.Integer(), nullable=True))
    op.add_column('tourneys', sa.Column('idowner', sa.Integer(), nullable=True))


def downgrade():
    op.drop_column('tourneys', 'idowner')
    op.drop_column('ratings', 'idowner')
    op.drop_column('players', 'idowner')
    op.drop_column('clubs', 'idowner')
    op.drop_column('championships', 'idowner')
