"""add external identity tables

Revision ID: 24ab8d11f014
Revises: 2bb1ba973f0b
Create Date: 2011-11-10 23:18:19.446844

"""

# downgrade revision identifier, used by Alembic.
revision = '24ab8d11f014'
down_revision = '2bb1ba973f0b'

from alembic.op import *
import sqlalchemy as sa

def upgrade():
    create_table('external_identities',
                 sa.Column('external_id', sa.Unicode(255), primary_key=True),
                 sa.Column('external_user_name', sa.Unicode(50), default=u''),
                 sa.Column('local_user_name', sa.Unicode(50),
                           sa.ForeignKey('users.user_name', onupdate='CASCADE',
                                      ondelete='CASCADE'), primary_key=True),
                 sa.Column('provider_name', sa.Unicode(50), default=u'',
                           primary_key=True),
                 sa.Column('access_token', sa.String(255), default=u''),
                 sa.Column('alt_token', sa.String(255), default=u''),
                 sa.Column('token_secret', sa.String(255), default=u'')
                 )


def downgrade():
    drop_table('external_identities')
