"""Add tags to forms.

Revision ID: 3c76c84ce8c0
Revises: 118823d0619
Create Date: 2014-03-24 15:19:17.163001

"""

# revision identifiers, used by Alembic.
revision = '3c76c84ce8c0'
down_revision = '118823d0619'

from alembic import op
import sqlalchemy as sa


INSERTS = """"""
DELETES = """"""


def iter_statements(stmts):
    for st in [x for x in stmts.split('\n') if x]:
        op.execute(st)


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('nm_form_tags',
    sa.Column('iid', sa.Integer(), nullable=True),
    sa.Column('tid', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['iid'], [u'forms.id'], ),
    sa.ForeignKeyConstraint(['tid'], ['tags.id'], )
    )
    ### end Alembic commands ###
    iter_statements(INSERTS)


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('nm_form_tags')
    ### end Alembic commands ###
    iter_statements(DELETES)
