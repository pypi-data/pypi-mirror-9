# :Progetto:  SoL -- Add delaytoppairing field to tourneys
# :Creato:    2014-09-03 17:31:11.962136
# :Autore:    Lele Gaifax <lele@metapensiero.it>
# :Licenza:   GNU General Public License version 3 or later
#

from alembic import op
import sqlalchemy as sa


revision = '4eece1d83ff'
down_revision = '31406b7040e'


def upgrade():
    op.add_column('tourneys', sa.Column('delaytoppairing', sa.SmallInteger(), nullable=False,
                                        server_default='1'))


def downgrade():
    op.drop_column('tourneys', 'delaytoppairing')
