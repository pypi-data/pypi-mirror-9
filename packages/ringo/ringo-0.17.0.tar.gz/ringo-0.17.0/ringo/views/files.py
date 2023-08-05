import logging
import mimetypes
from pyramid.response import FileIter
from pyramid.view import view_config

from ringo.views.base import create, update, read
from ringo.lib.helpers import import_model, get_action_routename
File = import_model('ringo.model.file.File')

log = logging.getLogger(__name__)

def save_file(request, item):
    """Helper function which is called after the validation of the form
    succeeds. The function will get the data from the file from the
    request and set it in the model including size and mime type.
    Addiotionally it will set the filename based on the uploaded file if
    no other name is given."""
    try:
        # Rewind file
        request.POST.get('file').file.seek(0)
        data = request.POST.get('file').file.read()
        filename = request.POST.get('file').filename
        item.data = data
        item.size = len(data)
        item.mime = mimetypes.guess_type(filename)[0]
        if not request.POST.get('name'):
            item.name = filename
    except AttributeError:
        # Will be raised if the user submits no file.
        pass
    return item

@view_config(route_name=get_action_routename(File, 'create'),
             renderer='/default/create.mako',
             permission='create')
def create_(request):
    return create(request, callback=save_file)


@view_config(route_name=get_action_routename(File, 'update'),
             renderer='/default/update.mako',
             permission='update')
def update_(request):
    return update(request, callback=save_file)


@view_config(route_name=get_action_routename(File, 'download'),
             permission='download')
def download(request):
    result = read(request)
    item = result['item']
    response = request.response
    response.content_type = str(item.mime)
    response.content_disposition = 'attachment; filename="%s"' % item.name
    response.body = item.data
    return response
