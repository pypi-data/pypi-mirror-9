import logging
from pyramid.view import view_config
from ringo.lib.helpers import get_action_routename
from ringo.model.news import News
from ringo.views.base.read import rest_read, read
from ringo.views.base.update import update

log = logging.getLogger(__name__)


def _mark_news_as_read(request, item):
    """Will mark the given news item as read for the current user of the
    request.

    :request: current request
    :item: news item
    :returns: news item

    """
    # A news item will be shown for all users in item.users. To make it
    # read we remove the entry of the current user from the item.users
    # list.
    users = item.users
    users.remove(request.user)
    return item


def read_callback(request, item):
    """Callback which is called right after the news item has been loaded.

    :request: current request
    :item: the news item
    :returns: news item

    """
    item = _mark_news_as_read(request, item)
    return item


@view_config(route_name=get_action_routename(News, 'markasread', prefix="rest"),
             renderer='json',
             request_method="PUT",
             permission='read')
def rest_markasread(request):
    return rest_read(request, callback=read_callback)


# FIXME: Overwritten templates for News. These templates do not escape
# the header as it might contain links. This is a security risk! (ti)
# See https://bitbucket.org/ti/ringo/issue/66/add-link-fields-to-news-modul
# <2014-08-28 12:20>
@view_config(route_name=get_action_routename(News, 'read'),
             renderer='/news/read.mako',
             permission='read')
def read_(request):
    return read(request)

@view_config(route_name=get_action_routename(News, 'update'),
             renderer='/news/update.mako',
             permission='update')
def update_(request):
    return update(request)
