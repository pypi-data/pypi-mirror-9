# :Progetto:  SoL -- Add fields to handle final matches
# :Creato:    2014-08-31 09:04:26.338062
# :Autore:    Lele Gaifax <lele@metapensiero.it>
# :Licenza:   GNU General Public License version 3 or later
#

from alembic import op
import sqlalchemy as sa


revision = '31406b7040e'
down_revision = '45df481185'


def upgrade():
    op.add_column('matches', sa.Column('final', sa.Boolean(), nullable=False,
                                       server_default='0'))
    op.drop_index('matches_uk', table_name='matches')
    op.execute("CREATE UNIQUE INDEX matches_c1_vs_c2"
               " ON matches (idtourney, idcompetitor1, idcompetitor2)"
               " WHERE final=0")
    op.add_column('tourneys', sa.Column('finals', sa.SmallInteger(), nullable=True))
    op.add_column('tourneys', sa.Column('finalturns', sa.Boolean(), nullable=False,
                                        server_default='0'))
    op.add_column('tourneys', sa.Column('finalkind', sa.VARCHAR(10), nullable=False,
                                        server_default='simple'))


def downgrade():
    op.drop_column('tourneys', 'finalkind')
    op.drop_column('tourneys', 'finalturns')
    op.drop_column('tourneys', 'finals')
    op.drop_index('matches_c1_vs_c2', table_name='matches')
    op.create_index('matches_uk', 'matches', ['idtourney', 'idcompetitor1', 'idcompetitor2'],
                    unique=True)
    op.drop_column('matches', 'final')
