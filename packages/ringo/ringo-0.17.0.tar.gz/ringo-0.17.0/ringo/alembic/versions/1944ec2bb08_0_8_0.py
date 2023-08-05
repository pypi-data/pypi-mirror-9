"""0.8.0

Revision ID: 1944ec2bb08
Revises: 52da2632399e
Create Date: 2013-11-18 18:52:57.987877

"""

# revision identifiers, used by Alembic.
revision = '1944ec2bb08'
down_revision = '52da2632399e'

from alembic import op
import sqlalchemy as sa


INSERTS = """
INSERT INTO "modules" VALUES(10,'logs','ringo.model.log.Log','Log','Logs',NULL,NULL,'admin-menu');
INSERT INTO "actions" VALUES(43,10,'List','list','icon-list-alt',NULL);
INSERT INTO "actions" VALUES(44,10,'Create','create',' icon-plus',NULL);
INSERT INTO "actions" VALUES(45,10,'Read','read/{id}','icon-eye-open',NULL);
INSERT INTO "actions" VALUES(46,10,'Update','update/{id}','icon-edit',NULL);
INSERT INTO "actions" VALUES(47,10,'Delete','delete/{id}','icon-trash',NULL);
INSERT INTO "nm_action_roles" VALUES(45,2);
"""
DELETES = """
DELETE FROM modules where id = 10;
DELETE FROM actions where id = 43;
DELETE FROM actions where id = 44;
DELETE FROM actions where id = 45;
DELETE FROM actions where id = 46;
DELETE FROM actions where id = 47;
DELETE FROM "nm_action_roles" where aid=45;
"""


def iter_statements(stmts):
    for st in [x for x in stmts.split('\n') if x]:
        op.execute(st)


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('logs',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('gid', sa.Integer(), nullable=True),
    sa.Column('uid', sa.Integer(), nullable=True),
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.Column('updated', sa.DateTime(), nullable=True),
    sa.Column('author', sa.Text, nullable=True, default=None),
    sa.Column('category', sa.Integer, nullable=True, default=None),
    sa.Column('subject', sa.Text, nullable=False, default=None),
    sa.Column('text', sa.Text, nullable=True, default=None),
    sa.ForeignKeyConstraint(['gid'], ['usergroups.id'], ),
    sa.ForeignKeyConstraint(['uid'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    ### end Alembic commands ###
    iter_statements(INSERTS)


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('logs')
    ### end Alembic commands ###
    iter_statements(DELETES)
