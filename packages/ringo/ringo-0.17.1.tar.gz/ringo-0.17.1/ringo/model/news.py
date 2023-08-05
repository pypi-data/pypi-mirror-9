import sqlalchemy as sa
from ringo.model import Base
from ringo.model.base import BaseItem
from ringo.model.mixins import Owned, Meta


nm_news_user = sa.Table(
    'nm_news_user', Base.metadata,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('uid', sa.Integer, sa.ForeignKey('users.id')),
    sa.Column('nid', sa.Integer, sa.ForeignKey('news.id'))
)
"""Table to store the unread (visible) news for a user. If the user has read
the news the entry in this table can be removed"""


class News(BaseItem, Meta, Owned, Base):
    __tablename__ = 'news'
    _modul_id = 9
    id = sa.Column(sa.Integer, primary_key=True)
    subject = sa.Column(sa.String)
    text = sa.Column(sa.Text)

    users = sa.orm.relationship("User",
                                secondary=nm_news_user,
                                backref='news')
