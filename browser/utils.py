import os

from django.conf import settings
from django.http import HttpResponse
from django.utils.deprecation import MiddlewareMixin


class IpWhitelistMiddleware(MiddlewareMixin):
    def process_request(self, request):
        ip = request.META['REMOTE_ADDR']

        if ip not in settings.ALLOWED_IPS:
            return HttpResponse("403: Brak dostępu")


def parse_path(path: str):
    """
    sprawdza, czy ścieżka jest koszerna i zwraca pełną
    :param path: path relatywny
    :return: pełny path
    """
    p = os.path.join(settings.BROWSEABLE_DIR, path)

    # wymusza rozpoczynanie folderu od BROWSEABLE_DIR z ustawień
    # django samo wycina próby path traversal
    if not p.startswith(settings.BROWSEABLE_DIR):
        return settings.BROWSEABLE_DIR

    return p


def render_path(path, *args):
    """
    zwraca ładną ścieżkę
    :param path: ścieżka
    :param args: foldery/pliki do dorzucenia do ścieżki
    :return:
    """
    path = os.path.join(path, *args)

    return path if path.endswith('/') or path.endswith(settings.SOUND_EXTENSIONS) else path + "/"


def split_path_for_breadcrumbs(path: str):
    """
    dzieli ścieżkę na części
    https://pl.wikipedia.org/wiki/Okruszki_chleba_(nawigacja)
    :param path: ścieżka
    :return: tuple(nazwa folderu, ścieżka)
    """
    if path is None:
        return None

    result = []
    fullpath = ""
    for curr in path.split('/'):
        fullpath += "%s/" % curr

        # z jakiegoś powodu pierwszy slash robił się pierwszym elementem
        if len(curr) > 1:
            # i breadcrumb nie powinien wyświetlać pliku
            if not curr.endswith(settings.SOUND_EXTENSIONS):
                result.append(
                    (curr, fullpath)
                )

    return result


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
