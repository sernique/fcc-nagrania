import os
from wsgiref.util import FileWrapper

from django.http import Http404, StreamingHttpResponse, HttpResponse
from django.shortcuts import render, redirect

from .utils import render_path, split_path_for_breadcrumbs, parse_path


def browse(request, path=""):
    fullpath = parse_path(path)

    try:
        items = os.listdir(fullpath)
    except NotADirectoryError:
        return redirect('show', path=path)

    dirs = sorted(
        list(filter(lambda d: os.path.isdir(os.path.join(fullpath, d)), items)),
        key=str.lower
    )
    files = sorted(
        list(filter(lambda d: os.path.isfile(os.path.join(fullpath, d)), items)),
        key=str.lower
    )

    context = {
        'previous_path': render_path(path, os.pardir),
        'breadcrumbs': split_path_for_breadcrumbs(render_path(path)),
        'dirs': [{'name': d, 'path': render_path(path, d)} for d in dirs],
        'files': [{'name': f, 'ext': os.path.splitext(f)[-1][1:], 'path': render_path(path, f)} for f in files]
    }

    return render(request, 'browser/browse.html', context)


def search(request):
    pass


def show(request, path):
    if not path.endswith(('mp3', 'wav')):
        # tylko dźwięki pozwól pobierać
        raise Http404()

    context = {
        'breadcrumbs': split_path_for_breadcrumbs(render_path(path)),
        'name': os.path.basename(path),
        'path': path,
        'ext': os.path.splitext(path)[-1][1:]
    }

    return render(request, 'browser/show.html', context)


def stream_file(request, path):
    return get_file(request, path, stream=True)


def get_file(request, path, stream=False):
    fullpath = parse_path(path)

    if stream:
        response = StreamingHttpResponse(
            FileWrapper(open(fullpath, 'rb'), 8192),
            content_type="audio/mpeg"
        )
    else:
        response = HttpResponse(
            open(fullpath, 'rb'), content_type='application/force-download'
        )
    response['Content-Dispositon'] = 'attachment; filename=%s' % os.path.basename(path)
    response['Content-Length'] = os.path.getsize(fullpath)

    return response


def index(request):
    return redirect('browser')
