from django.contrib import admin
from django.http import HttpRequest
from django.shortcuts import render
from django.urls import reverse

from apps.biography.models import Biography, TimelineEvent
from apps.gallery.models import Photo
from apps.media_mentions.models import MediaMention
from apps.memories.models import Memory
from apps.videos.models import Video


def home_admin_view(request: HttpRequest):
    biography = Biography.objects.first()

    timeline_events = TimelineEvent.objects.all()[:3]

    gallery_photos = Photo.objects.filter(
        is_published=True,
    )[:6]

    featured_video = Video.objects.filter(
        is_published=True,
        is_featured=True,
    ).first()

    featured_mention = MediaMention.objects.filter(
        is_published=True,
        is_featured=True,
    ).first()

    featured_memory = Memory.objects.filter(
        status=Memory.Status.APPROVED,
        featured=True,
    ).first()

    context = {
        **admin.site.each_context(request),
        "title": "Головна",
        "biography": biography,
        "timeline_events": timeline_events,
        "gallery_photos": gallery_photos,
        "featured_video": featured_video,
        "featured_mention": featured_mention,
        "featured_memory": featured_memory,
        "biography_url": (
            reverse(
                "admin:biography_biography_change",
                args=[biography.pk],
            )
            if biography
            else reverse(
                "admin:biography_biography_add",
            )
        ),
        "life_url": reverse(
            "admin:biography_life",
        ),
        "photos_url": reverse(
            "admin:gallery_photo_changelist",
        ),
        "videos_url": reverse(
            "admin:videos_video_changelist",
        ),
        "publications_url": reverse(
            "admin:media_mentions_mediamention_changelist",
        ),
        "memories_url": reverse(
            "admin:memories_memory_changelist",
        ),
    }

    return render(
        request,
        "admin/home/dashboard.html",
        context,
    )
