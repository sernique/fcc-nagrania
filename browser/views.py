import logging
import os
from wsgiref.util import FileWrapper

import fs
from django.conf import settings
from django.http import Http404, StreamingHttpResponse, HttpResponse
from django.shortcuts import render, redirect

from .forms import SearchForm
from .utils import render_path, split_path_for_breadcrumbs, parse_path, get_client_ip

logger = logging.getLogger('django')


def list_files(request, path, dirs, files):
    if not fs.isdir(parse_path(path)):
        # jeśli folder jest plikiem, przejdź do widoku pliku
        return redirect('show', path=path)

    context = {
        # poprzednia ścieżka
        'previous_path': render_path(path, os.pardir),

        # nawigacja
        'breadcrumbs': split_path_for_breadcrumbs(render_path(path)),

        # lista folderów
        'dirs': [
            {
                'name': os.path.basename(d),
                'path': d.replace(settings.BROWSEABLE_DIR, '')
            } for d in dirs
        ],

        # lista plików
        'files': [
            {
                'name': os.path.basename(f),
                'ext': os.path.splitext(f)[-1][1:],
                'path': f.replace(settings.BROWSEABLE_DIR, '')
            } for f in files
        ]
    }

    return render(request, 'browser/browse.html', context)


def browse(request, path=""):
    fullpath = parse_path(path)

    try:
        # spróbuj pobrać listę plików
        items = [os.path.join(fullpath, item) for item in os.listdir(fullpath)]
    except NotADirectoryError:
        if not fs.isdir(parse_path(path)):
            # jeśli folder jest plikiem, przejdź do widoku pliku
            return redirect('show', path=path)

    # przefiltruj listę folderów i posortuj alfabetycznie
    dirs = sorted(
        list(filter(lambda d: os.path.isdir(d), items)),
        key=str.lower
    )

    # przefiltruj listę plików i posortuj alfabetycznie
    files = sorted(
        list(filter(lambda d: os.path.isfile(d), items)),
        key=str.lower
    )

    return list_files(request, path, dirs, files)


def search(request):
    form = SearchForm(request.POST)

    if request.POST and form.is_valid():
        # ścieżka domyślna
        path = parse_path(settings.BROWSEABLE_DIR)
        text = form.cleaned_data['text']

        logger.info('%s wyszukał "%s"' % (get_client_ip(request), text))

        # pliki
        files = []
        with open(settings.SEARCH_FILELIST, 'r') as file:
            for line in file:
                if text in line:
                    files.append(line.strip())

        files = sorted(
            files,
            # fs.find('*%s*' % text, path, recursive=True),
            key=str.lower
        )

        return list_files(request, '', [], files)
    else:
        return render(
            request,
            'browser/search.html',
            context={'form': form, 'breadcrumbs': None}
        )


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
        logger.info('%s streamował "%s"' % (get_client_ip(request), os.path.basename(fullpath)))
        # zwraca stream audio/mpeg
        response = StreamingHttpResponse(
            FileWrapper(open(fullpath, 'rb'), 8192),
            content_type="audio/mpeg"
        )
    else:
        logger.info('%s pobrał "%s"' % (get_client_ip(request), os.path.basename(fullpath)))
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
    return redirect('search')
