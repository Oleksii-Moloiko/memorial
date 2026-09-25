import ipaddress
import logging
import mimetypes
import socket
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse
from urllib.request import (
    HTTPRedirectHandler,
    Request,
    build_opener,
)
from uuid import uuid4

from django.core.files.base import ContentFile
from django.utils import timezone
from django.db import transaction


logger = logging.getLogger(__name__)

TIMEOUT_SECONDS = 6
MAX_HTML_BYTES = 1_500_000
MAX_IMAGE_BYTES = 8_000_000

ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/gif",
}


class PreviewMetaParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.images = {}

    def handle_starttag(self, tag, attrs):
        if tag.lower() != "meta":
            return

        values = {
            key.lower(): value
            for key, value in attrs
            if key and value
        }

        name = (
            values.get("property")
            or values.get("name")
            or ""
        ).lower()

        content = values.get("content", "").strip()

        if name in {
            "og:image",
            "og:image:url",
            "twitter:image",
            "twitter:image:src",
        } and content:
            self.images.setdefault(name, content)

    def get_image_url(self):
        for name in (
            "og:image",
            "og:image:url",
            "twitter:image",
            "twitter:image:src",
        ):
            if name in self.images:
                return self.images[name]

        return None


def _validate_public_url(url):
    parsed = urlparse(url)

    if (
        parsed.scheme not in {"http", "https"}
        or not parsed.hostname
    ):
        raise ValueError(
            "Підтримуються лише публічні HTTP/HTTPS URL."
        )

    port = parsed.port or (
        443 if parsed.scheme == "https" else 80
    )

    addresses = socket.getaddrinfo(
        parsed.hostname,
        port,
        type=socket.SOCK_STREAM,
    )

    for address in addresses:
        ip = ipaddress.ip_address(address[4][0])

        if not ip.is_global:
            raise ValueError(
                "Локальні та службові адреси заборонені."
            )


class SafeRedirectHandler(HTTPRedirectHandler):
    def redirect_request(
        self,
        req,
        fp,
        code,
        msg,
        headers,
        newurl,
    ):
        _validate_public_url(newurl)

        return super().redirect_request(
            req,
            fp,
            code,
            msg,
            headers,
            newurl,
        )


opener = build_opener(
    SafeRedirectHandler()
)


def _read_limited(response, limit):
    data = response.read(limit + 1)

    if len(data) > limit:
        raise ValueError(
            "Віддалений файл завеликий."
        )

    return data


def fetch_preview_image(mention):
    """
    Завантажує og:image / twitter:image.

    Ручне preview_image завжди має пріоритет.
    """

    if mention.preview_image or not mention.url:
        return False

    try:
        _validate_public_url(
            mention.url
        )

        page_request = Request(
            mention.url,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 "
                    "MemorialPreviewBot/1.0"
                ),
                "Accept": (
                    "text/html,"
                    "application/xhtml+xml"
                ),
            },
        )

        with opener.open(
            page_request,
            timeout=TIMEOUT_SECONDS,
        ) as response:
            content_type = (
                response.headers.get_content_type()
            )

            if content_type not in {
                "text/html",
                "application/xhtml+xml",
            }:
                return False

            html_bytes = _read_limited(
                response,
                MAX_HTML_BYTES,
            )

            charset = (
                response.headers.get_content_charset()
                or "utf-8"
            )

            final_page_url = response.geturl()

        parser = PreviewMetaParser()

        parser.feed(
            html_bytes.decode(
                charset,
                errors="replace",
            )
        )

        image_url = parser.get_image_url()

        if not image_url:
            return False

        image_url = urljoin(
            final_page_url,
            image_url,
        )

        _validate_public_url(
            image_url
        )

        image_request = Request(
            image_url,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 "
                    "MemorialPreviewBot/1.0"
                ),
                "Accept": "image/*",
            },
        )

        with opener.open(
            image_request,
            timeout=TIMEOUT_SECONDS,
        ) as response:
            content_type = (
                response.headers.get_content_type()
            )

            if (
                content_type
                not in ALLOWED_IMAGE_TYPES
            ):
                return False

            image_bytes = _read_limited(
                response,
                MAX_IMAGE_BYTES,
            )

            final_image_url = (
                response.geturl()
            )

        extension = (
            mimetypes.guess_extension(
                content_type
            )
            or ".jpg"
        )

        if extension == ".jpe":
            extension = ".jpg"

        filename = (
            f"preview-{uuid4().hex}"
            f"{extension}"
        )

        old_name = (
            mention.auto_preview_image.name
            if mention.auto_preview_image
            else None
        )

        mention.auto_preview_image.save(
            filename,
            ContentFile(image_bytes),
            save=False,
        )

        mention.preview_fetched_from = (
            final_image_url
        )

        mention.preview_fetched_at = (
            timezone.now()
        )

        with transaction.atomic():
            mention.save(
                update_fields=(
                    "auto_preview_image",
                    "preview_fetched_from",
                    "preview_fetched_at",
                )
            )

        if (
            old_name
            and old_name
            != mention.auto_preview_image.name
        ):
            mention.auto_preview_image.storage.delete(
                old_name
            )

        return True

    except Exception:
        logger.exception(
            "Не вдалося отримати прев'ю "
            "для MediaMention id=%s",
            mention.pk,
        )

        return False