import re
from urllib.parse import urljoin

from django.conf import settings
from django.urls import reverse
from django.utils import translation
from django.utils.html import strip_tags


def absolute_url(request, path):
    base = getattr(settings, "SITE_URL", "").rstrip("/") or request.build_absolute_uri(
        "/"
    ).rstrip("/")
    return urljoin(base + "/", path)


DURATION_RE = re.compile(r"^(?:(\d+):)?(\d{1,2}):(\d{2})$")


def iso_duration(value):
    """'03:42' -> 'PT0H3M42S'; '1:02:03' -> 'PT1H2M3S'."""
    match = DURATION_RE.match((value or "").strip())
    if not match:
        return None
    hours, minutes, seconds = (int(part or 0) for part in match.groups())
    return f"PT{hours}H{minutes}M{seconds}S"


def person_id(request):
    with translation.override("uk"):
        return absolute_url(request, reverse("pages:home")) + "#person"


def build_person(request, biography):
    if not biography or not biography.full_name.strip():
        return None

    # Один ідентифікатор людини для обох мовних версій.
    identity = person_id(request)

    data = {
        "@context": "https://schema.org",
        "@type": "Person",
        "@id": identity,
        "name": biography.full_name,
        "url": absolute_url(request, reverse("pages:home")),
    }

    if biography.portrait:
        responsive = biography.responsive_portrait
        image_url = responsive["src"] if responsive else biography.portrait.url
        data["image"] = absolute_url(request, image_url)

    if biography.birth_date:
        data["birthDate"] = biography.birth_date.isoformat()

    if biography.death_date:
        data["deathDate"] = biography.death_date.isoformat()

    if biography.rank:
        data["jobTitle"] = biography.rank

    description = strip_tags(biography.intro_text or "").strip()
    if description:
        data["description"] = description

    return data


def build_breadcrumbs(request, site_settings):
    match = getattr(request, "resolver_match", None)
    if not match or not site_settings:
        return None

    title_fields = {
        "pages:life": "life_title",
        "pages:service": "service_title",
        "pages:photos": "photos_title",
        "pages:videos": "videos_title",
        "pages:memories": "memories_title",
    }
    title_field = title_fields.get(match.view_name)
    if not title_field:
        return None

    home_name = (site_settings.home_title or "").strip()
    page_name = (getattr(site_settings, title_field, "") or "").strip()
    if not home_name or not page_name:
        return None

    page_url = absolute_url(request, reverse(match.view_name))

    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "@id": page_url + "#breadcrumbs",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": 1,
                "name": home_name,
                "item": absolute_url(request, reverse("pages:home")),
            },
            {
                "@type": "ListItem",
                "position": 2,
                "name": page_name,
                "item": page_url,
            },
        ],
    }


def build_image_gallery(request, photos, name, description=""):
    images = []
    for photo in photos:
        if not photo.image:
            continue
        image = {
            "@type": "ImageObject",
            "contentUrl": absolute_url(request, photo.image.url),
        }
        caption = (photo.caption or "").strip()
        if caption:
            image["caption"] = caption
        images.append(image)

    if not images:
        return None

    data = {
        "@context": "https://schema.org",
        "@type": "ImageGallery",
        "url": absolute_url(request, request.path),
        "name": name,
        "about": {"@id": person_id(request)},
        "image": images,
    }
    if description:
        data["description"] = description
    return data


def build_video_object(request, video):
    if not video.thumbnail:
        return None

    responsive = video.responsive_thumbnail
    thumbnail = responsive["src"] if responsive else video.thumbnail.url
    description = strip_tags(video.description or "").strip()

    data = {
        "@type": "VideoObject",
        "name": video.title,
        "description": description or video.title,
        "thumbnailUrl": absolute_url(request, thumbnail),
        "uploadDate": video.created_at.isoformat(),
        "contentUrl": absolute_url(request, video.video_file.url),
        "about": {"@id": person_id(request)},
    }

    duration = iso_duration(video.duration)
    if duration:
        data["duration"] = duration

    transcript = (video.transcript or "").strip()
    if transcript:
        data["transcript"] = transcript

    return data


def build_videos(request, videos):
    items = [item for item in (build_video_object(request, v) for v in videos) if item]
    if not items:
        return None
    return {"@context": "https://schema.org", "@graph": items}
