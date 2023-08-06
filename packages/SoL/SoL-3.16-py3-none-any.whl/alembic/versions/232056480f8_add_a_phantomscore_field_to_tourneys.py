# :Progetto:  SoL -- Add a phantomscore field to tourneys
# :Creato:    2014-05-16 12:55:33.896401
# :Autore:    Lele Gaifax <lele@metapensiero.it>
# :Licenza:   GNU General Public License version 3 or later
#

from alembic import op
import sqlalchemy as sa


revision = '232056480f8'
down_revision = '47989246a0c'


def upgrade():
    op.add_column('tourneys', sa.Column('phantomscore', sa.SmallInteger(),
                                        nullable=False, server_default='25'))


def downgrade():
    op.drop_column('tourneys', 'phantomscore')
