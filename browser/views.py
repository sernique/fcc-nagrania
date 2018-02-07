import os
from wsgiref.util import FileWrapper

from django.http import Http404, StreamingHttpResponse, HttpResponse
from django.shortcuts import render, redirect

from .utils import render_path, split_path_for_breadcrumbs, parse_path


def browse(request, path=""):
    fullpath = parse_path(path)

    try:
        # spróbuj pobrać listę plików
        items = os.listdir(fullpath)
    except NotADirectoryError:
        # jeśli folder jest plikiem, przejdź do widoku pliku
        return redirect('show', path=path)

    # przefiltruj listę folderów i posortuj alfabetycznie
    dirs = sorted(
        list(filter(lambda d: os.path.isdir(os.path.join(fullpath, d)), items)),
        key=str.lower
    )
    # przefiltruj listę plików i posortuj alfabetycznie
    files = sorted(
        list(filter(lambda d: os.path.isfile(os.path.join(fullpath, d)), items)),
        key=str.lower
    )

    context = {
        # poprzednia ścieżka
        'previous_path': render_path(path, os.pardir),

        # nawigacja
        'breadcrumbs': split_path_for_breadcrumbs(render_path(path)),

        # lista folderów
        # { name: nazwa, path: ścieżka }
        'dirs': [{'name': d, 'path': render_path(path, d)} for d in dirs],

        # lista plików
        # { name: nazwa, ext: rozszerzenie, path: ścieżka }
        'files': [{'name': f, 'ext': os.path.splitext(f)[-1][1:], 'path': render_path(path, f)} for f in files]
    }

    return render(request, 'browser/browse.html', context)


def search(request):
    pass


def show(request, path):
    if not path.endswith(('mp3', 'wav')):
        # pokazuj tylko dźwięki, dla innych 404
        raise Http404()

    context = {
        # nawigacja
        'breadcrumbs': split_path_for_breadcrumbs(render_path(path)),

        # nazwa pliku
        'name': os.path.basename(path),

        # ścieżka
        'path': path,

        # rozszerzenie
        'ext': os.path.splitext(path)[-1][1:]
    }

    return render(request, 'browser/show.html', context)


def stream_file(request, path):
    # zamiast pliku zwróci plik streamowany przez http
    return get_file(request, path, stream=True)


def get_file(request, path, stream=False):
    fullpath = parse_path(path)

    if stream:
        # zwraca stream audio/mpeg
        response = StreamingHttpResponse(
            FileWrapper(open(fullpath, 'rb'), 8192),
            content_type="audio/mpeg"
        )
    else:
        # zwraca plik do pobrania
        response = HttpResponse(
            open(fullpath, 'rb'), content_type='application/force-download'
        )

    # nagłówki http
    response['Content-Dispositon'] = 'attachment; filename=%s' % os.path.basename(path)
    response['Content-Length'] = os.path.getsize(fullpath)

    return response


def index(request):
    # przekierowanie / na domyślny folder
    # we flasku nie trzeba było cudować...
    return redirect('browser')
