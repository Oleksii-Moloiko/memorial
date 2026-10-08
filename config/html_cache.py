import hashlib
import json
import re

from django.conf import settings
from django.utils.cache import (
    get_conditional_response,
    patch_cache_control,
    patch_vary_headers,
)


class PublicHtmlCacheMiddleware:
    PAGE_NAMES = {
        "pages:home",
        "pages:life",
        "pages:service",
        "pages:photos",
        "pages:videos",
        "pages:memories",
    }

    CSRF_INPUT = re.compile(
        rb'(<input\b[^>]*\bname="csrfmiddlewaretoken"'
        rb'[^>]*\bvalue=")[A-Za-z0-9]{64}(")'
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        match = request.resolver_match

        if not match or match.view_name not in self.PAGE_NAMES:
            return response

        patch_vary_headers(response, ("Cookie", "Accept-Language"))

        personalized = (
            getattr(getattr(request, "user", None), "is_authenticated", False)
            or settings.SESSION_COOKIE_NAME in request.COOKIES
            or "messages" in request.COOKIES
            or settings.SESSION_COOKIE_NAME in response.cookies
            or "messages" in response.cookies
        )

        if (
            request.method not in ("GET", "HEAD")
            or response.status_code != 200
            or personalized
            or response.streaming
            or not response.get("Content-Type", "").startswith("text/html")
        ):
            patch_cache_control(
                response,
                private=True,
                no_store=True,
                no_cache=True,
                max_age=0,
            )
            return response

        # Поважаємо заборону кешування, задану іншими компонентами.
        if (
            "no-store" in response.get("Cache-Control", "").lower()
            or "*" in response.get("Vary", "").split(",")
            or response.get("Content-Encoding")
        ):
            return response

        patch_cache_control(response, private=True, no_cache=True)

        secret = request.META.get("CSRF_COOKIE", "")
        content = response.content

        if secret:
            # Нормалізуємо лише копію для хешування.
            content = self.CSRF_INPUT.sub(rb"\1<csrf>\2", content)

        context = json.dumps(
            [
                request.get_full_path(),
                getattr(request, "LANGUAGE_CODE", ""),
                secret,
                sorted(
                    (key, value)
                    for key, value in request.COOKIES.items()
                    if key != settings.CSRF_COOKIE_NAME
                ),
            ],
            ensure_ascii=True,
        ).encode("utf-8")

        digest = hashlib.sha256(context + b"\0" + content).hexdigest()
        etag = f'W/"{digest}"'
        response["ETag"] = etag

        # Перший візит або зміна CSRF-cookie потребує повного HTML.
        if secret and request.COOKIES.get(settings.CSRF_COOKIE_NAME) != secret:
            return response

        conditional = get_conditional_response(
            request,
            etag=etag,
            response=response,
        )

        if conditional is not response:
            # Зберігаємо заголовки безпеки, мови та кешування.
            excluded = {
                "content-type",
                "content-length",
                "content-encoding",
                "transfer-encoding",
            }
            for name, value in response.items():
                if name.lower() not in excluded:
                    conditional[name] = value
            conditional.cookies = response.cookies

        return conditional