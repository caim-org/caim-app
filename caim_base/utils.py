from django.conf import settings


def full_url(path):
    if path.startswith("http://") or path.startswith("https://"):
        return path
    url_prefix = settings.URL_PREFIX or ""
    return f"{url_prefix}{path}"
