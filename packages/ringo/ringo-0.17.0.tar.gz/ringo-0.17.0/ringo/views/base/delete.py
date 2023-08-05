import logging
from pyramid.httpexceptions import HTTPFound
from ringo.lib.sql.cache import invalidate_cache
from ringo.lib.renderer import ConfirmDialogRenderer
from ringo.lib.helpers import (
    get_action_routename,
    get_item_modul
)
from ringo.views.response import JSONResponse
from ringo.views.request import (
    handle_params,
    handle_history,
    is_confirmed,
    get_item_from_request
)
from ringo.views.base.list_ import set_bundle_action_handler

log = logging.getLogger(__name__)


def _handle_redirect(request):
    """Will return a redirect.

    :request: Current request
    :returns: Redirect

    """
    clazz = request.context.__model__
    backurl = request.session.get('%s.backurl' % clazz)
    if backurl:
        # Redirect to the configured backurl.
        del request.session['%s.backurl' % clazz]
        request.session.save()
        return HTTPFound(location=backurl)
    else:
        # Redirect to the list view.
        route_name = get_action_routename(clazz, 'list')
        url = request.route_path(route_name)
        return HTTPFound(location=url)


def _handle_delete_request(request, items):
    clazz = request.context.__model__
    _ = request.translate
    if request.method == 'POST' and is_confirmed(request):
        for item in items:
            request.db.delete(item)
        item_label = get_item_modul(request, clazz).get_label(plural=True)
        mapping = {'item_type': item_label, 'num': len(items)}
        msg = _('Deleted ${num} ${item_type} successfull.', mapping=mapping)
        log.info(msg)
        request.session.flash(msg, 'success')
        # Invalidate cache
        invalidate_cache()
        # Handle redirect after success.
        return _handle_redirect(request)
    else:
        renderer = ConfirmDialogRenderer(request, clazz, 'delete')
        rvalue = {}
        rvalue['dialog'] = renderer.render(items)
        rvalue['clazz'] = clazz
        rvalue['item'] = items
        return rvalue


def delete(request):
    item = get_item_from_request(request)
    handle_history(request)
    handle_params(request)
    return _handle_delete_request(request, [item])


def rest_delete(request):
    """Deletes an item of type clazz. The item is deleted based on the
    unique id value provided in the matchtict object in the current
    DELETE request. The data will be deleted without any futher confirmation!

    :clazz: Class of item to delete
    :request: Current request
    :returns: JSON object.
    """
    item = get_item_from_request(request)
    request.db.delete(item)
    return JSONResponse(True, item)

set_bundle_action_handler("delete", _handle_delete_request)
