# :Progetto:  SoL -- Allow parametric outcomes computation
# :Creato:    2014-06-14 18:09:36.522702
# :Autore:    Lele Gaifax <lele@metapensiero.it>
# :Licenza:   GNU General Public License version 3 or later
#

from alembic import op
import sqlalchemy as sa


revision = '26651827d0f'
down_revision = '15282abff26'


def upgrade():
    op.add_column('ratings', sa.Column('outcomes', sa.VARCHAR(length=10),
                                       nullable=False, server_default='guido'))


def downgrade():
    op.drop_column('ratings', 'outcomes')
