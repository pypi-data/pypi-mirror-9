<%!
import re

%>"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision}
Create Date: ${create_date}

"""

# revision identifiers, used by Alembic.
revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}

from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

def upgrade(engine_name):
    globals()['upgrade_{}'.format(engine_name)]()


def downgrade(engine_name):
    globals()['downgrade_{}'.format(engine_name)]()

<%
    db_names = config.get_main_option('databases')
%>
% for db_name in re.split(r',\s*', db_names):
# Upgrade/downgrade functions for ${db_name}

def upgrade_${db_name}():
    ${context.get('{}_upgrades'.format(db_name), "pass")}


def downgrade_${db_name}():
    ${context.get('{}_downgrades'.format(db_name), "pass")}

% endfor
