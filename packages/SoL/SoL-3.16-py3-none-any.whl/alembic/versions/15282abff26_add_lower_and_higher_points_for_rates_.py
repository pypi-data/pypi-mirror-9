# :Progetto:  SoL -- Add lower and higher points for rates interpolation
# :Creato:    2014-06-09 22:05:26.328537
# :Autore:    Lele Gaifax <lele@metapensiero.it>
# :Licenza:   GNU General Public License version 3 or later
#

from alembic import op
import sqlalchemy as sa


revision = '15282abff26'
down_revision = '232056480f8'


def upgrade():
    op.add_column('ratings', sa.Column('higher_rate', sa.SmallInteger(),
                                       nullable=False, server_default='2600'))
    op.add_column('ratings', sa.Column('lower_rate', sa.SmallInteger(),
                                       nullable=False, server_default='1600'))


def downgrade():
    op.drop_column('ratings', 'lower_rate')
    op.drop_column('ratings', 'higher_rate')
