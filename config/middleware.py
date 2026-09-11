from django.utils import translation


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