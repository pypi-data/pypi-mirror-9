# :Progetto:  SoL -- Add inherit flag to ratings
# :Creato:    2014-04-09 19:13:24.041808
# :Autore:    Lele Gaifax <lele@metapensiero.it>
# :Licenza:   GNU General Public License version 3 or later
#

from alembic import op
import sqlalchemy as sa
from sol.models import Rating

revision = '47989246a0c'
down_revision = None

_rating_t = Rating.__table__

def upgrade():
    op.add_column('ratings', sa.Column('inherit', sa.Boolean()))
    op.execute(_rating_t.update() .values({'inherit': True}))


def downgrade():
    op.drop_column('ratings', 'inherit')
