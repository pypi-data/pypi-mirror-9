"""bigger identity datatypes

Revision ID: 2d472fe79b95
Revises: 264049f80948
Create Date: 2012-02-19 17:24:24.422312

"""

# revision identifiers, used by Alembic.
revision = '2d472fe79b95'
down_revision = '264049f80948'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.alter_column('external_identities', 'external_id',
                    type_=sa.String(255), existing_type=sa.String(50))
    op.alter_column('external_identities', 'external_user_name',
                    type_=sa.String(255), existing_type=sa.String(50))

def downgrade():
    pass