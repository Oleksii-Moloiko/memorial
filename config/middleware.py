from urllib.parse import urlsplit

from django.conf import settings
from django.http import HttpResponsePermanentRedirect
from django.utils import translation

class CanonicalHostMiddleware:
    """
    Redirect every non-canonical host/scheme to SITE_URL.

    Example:
    https://www.example.com/life/?foo=bar
    ->
    https://example.com/life/?foo=bar
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        site_url = getattr(settings, "SITE_URL", "")

        if not site_url:
            return self.get_response(request)

        parsed = urlsplit(site_url)

        canonical_scheme = parsed.scheme or "https"
        canonical_host = parsed.netloc

        current_host = request.get_host()

        if (
            current_host != canonical_host
            or request.scheme != canonical_scheme
        ):
            destination = (
                f"{canonical_scheme}://"
                f"{canonical_host}"
                f"{request.get_full_path()}"
            )

            return HttpResponsePermanentRedirect(destination)

        return self.get_response(request)

class AdminUkrainianLocaleMiddleware:
    """
    Keep the Django Admin interface in Ukrainian.

    The public site language is controlled separately and may be UK or EN.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.path_info.startswith("/admin/"):
            return self.get_response(request)

        with translation.override("uk"):
            request.LANGUAGE_CODE = "uk"
            return self.get_response(request)