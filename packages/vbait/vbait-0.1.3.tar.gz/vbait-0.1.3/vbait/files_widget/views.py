import json
from django.core.urlresolvers import reverse

from django.http import Http404, HttpResponse, HttpResponseBadRequest
from django.conf import settings
from django.template.loader import render_to_string
from django.contrib.auth.decorators import permission_required

from files import save_upload
from translate import trans


@permission_required('files_widget.can_upload_files')
def upload(request):
    if not request.method == 'POST':
        raise Http404

    # if request.is_ajax():
    #     # the file is stored raw in the request
    #     upload = request
    #     is_raw = True
    #     # AJAX Upload will pass the filename in the querystring if it is the "advanced" ajax upload
    #     try:
    #         filename = request.GET['files[0]']
    #     except KeyError:
    #         return HttpResponseBadRequest(json.dumps({
    #             'success': False,
    #             'message': 'Error while uploading file',
    #         }))
    # not an ajax upload, so it was the "basic" iframe version with submission via form
    # else:
    is_raw = False
    if len(request.FILES) == 1:
        upload = request.FILES.values()[0]
    else:
        return HttpResponseBadRequest(json.dumps({
            'success': False,
            'message': 'Error while uploading file.',
        }))
    filename = trans(upload.name)
    
    path_to_file = save_upload(upload, filename, is_raw, request.user)
    MEDIA_URL = settings.MEDIA_URL

    if 'preview_size' in request.POST:
        preview_size = request.POST['preview_size']
    else:
        preview_size = '64'

    return HttpResponse(json.dumps({
        'success': True,
        'imagePath': path_to_file,
        'thumbnailPath': render_to_string('files_widget/includes/thumbnail.html', locals()),
    }))

@permission_required('files_widget.can_upload_files')
def thumbnail_url(request):
    if not 'img' in request.GET or not 'preview_size' in request.GET:
        raise Http404
    return HttpResponse(reverse('generate_image', args=[request.GET['img']]) + "?wid=%s&hei=%s&cache=1" %
                        (request.GET['preview_size'], request.GET['preview_size']))
