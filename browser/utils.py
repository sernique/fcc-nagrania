import os

from django.conf import settings


def parse_path(path: str):
    p = os.path.join(settings.BROWSEABLE_DIR, path)

    # wymusza rozpoczynanie folderu od BROWSEABLE_DIR z ustawień
    # django samo wycina próby path traversal
    if not p.startswith(settings.BROWSEABLE_DIR):
        return settings.BROWSEABLE_DIR

    return p


def render_path(path, *args):
    path = os.path.join(path, *args)

    return path if path.endswith(("/", "mp3", "wav")) else path + "/"


def split_path_for_breadcrumbs(path: str):
    # tutaj to łatwiejsze niż w templatce
    result = []
    fullpath = ""
    for curr in path.split('/'):
        fullpath += "%s/" % curr
        result.append(
            (curr, fullpath)
        )

    return result
