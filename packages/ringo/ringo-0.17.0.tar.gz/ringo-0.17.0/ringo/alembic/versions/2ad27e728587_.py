"""Added comment module

Revision ID: 2ad27e728587
Revises: 1944ec2bb08
Create Date: 2014-01-02 11:26:43.782383

"""

# revision identifiers, used by Alembic.
revision = '2ad27e728587'
down_revision = '1944ec2bb08'

from alembic import op
import sqlalchemy as sa


INSERTS = """
INSERT INTO "modules" VALUES(11,'comments','ringo.model.comment.Comment','Comment','Comments',NULL,NULL,'hidden');
INSERT INTO "actions" VALUES(48,11,'List','list','icon-list-alt',NULL);
INSERT INTO "actions" VALUES(49,11,'Create','create',' icon-plus',NULL);
INSERT INTO "actions" VALUES(50,11,'Read','read/{id}','icon-eye-open',NULL);
INSERT INTO "actions" VALUES(51,11,'Update','update/{id}','icon-edit',NULL);
INSERT INTO "actions" VALUES(52,11,'Delete','delete/{id}','icon-trash',NULL);
"""

DELETES = """
DELETE FROM actions WHERE id = 48;
DELETE FROM actions WHERE id = 49;
DELETE FROM actions WHERE id = 50;
DELETE FROM actions WHERE id = 51;
DELETE FROM actions WHERE id = 52;
DELETE FROM modules WHERE id = 11;
"""


def iter_statements(stmts):
    for st in [x for x in stmts.split('\n') if x]:
        op.execute(st)


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('comments',
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.Column('updated', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('text', sa.Text(), nullable=True),
    sa.Column('parent_id', sa.Integer(), nullable=True),
    sa.Column('gid', sa.Integer(), nullable=True),
    sa.Column('uid', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['gid'], ['usergroups.id'], ),
    sa.ForeignKeyConstraint(['parent_id'], ['comments.id'], ),
    sa.ForeignKeyConstraint(['uid'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    ### end Alembic commands ###
    iter_statements(INSERTS)


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('comments')
    ### end Alembic commands ###
    iter_statements(DELETES)
