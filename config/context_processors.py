from urllib.parse import urljoin

from django.conf import settings
from django.db.utils import OperationalError, ProgrammingError
from django.urls import reverse
from django.utils import translation


def site_settings(request):
    try:
        from apps.core.models import SiteSettings

        settings_object = SiteSettings.load()
    except (OperationalError, ProgrammingError):
        settings_object = None

    return {"site_settings": settings_object}


def seo_urls(request):
    resolver_match = getattr(request, "resolver_match", None)

    if not resolver_match or not resolver_match.view_name:
        return {}

    view_name = resolver_match.view_name

    try:
        with translation.override("uk"):
            uk_path = reverse(
                view_name,
                args=resolver_match.args,
                kwargs=resolver_match.kwargs,
            )

        with translation.override("en"):
            en_path = reverse(
                view_name,
                args=resolver_match.args,
                kwargs=resolver_match.kwargs,
            )
    except Exception:
        return {}

    base_url = settings.SITE_URL

    if base_url:
        uk_url = f"{base_url}{uk_path}"
        en_url = f"{base_url}{en_path}"

        static_path = (
            f"/{settings.STATIC_URL.strip('/')}/"
            "images/og-default.jpg"
        )

        if base_url:
            uk_url = f"{base_url}{uk_path}"
            en_url = f"{base_url}{en_path}"
            default_og_image_url = (
                f"{base_url}{static_path}"
            )
        else:
            uk_url = request.build_absolute_uri(uk_path)
            en_url = request.build_absolute_uri(en_path)
            default_og_image_url = (
                request.build_absolute_uri(static_path)
            )
    else:
        uk_url = request.build_absolute_uri(uk_path)
        en_url = request.build_absolute_uri(en_path)

        default_og_image_url = request.build_absolute_uri(
            f"{settings.STATIC_URL}images/og-default.jpg"
        )

    current_language = translation.get_language()

    canonical_url = en_url if current_language == "en" else uk_url

    return {
        "canonical_url": canonical_url,
        "hreflang_uk": uk_url,
        "hreflang_en": en_url,
        "hreflang_x_default": uk_url,
        "default_og_image_url": default_og_image_url,
    }