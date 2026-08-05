from django.shortcuts import render

from apps.biography.models import Biography, TimelineEvent
from apps.gallery.models import Photo
from apps.media_mentions.models import MediaMention
from apps.memories.models import Memory
from apps.seo.models import SeoPage
from apps.videos.models import Video


def _seo_context(page_key):
    """Пласкі seo_title/seo_description/seo_image — саме так їх очікує
    includes/seo_meta.html. Якщо SeoPage для сторінки ще не заповнена
    в адмінці, шаблон сам підставляє дефолти через |default."""
    seo_page = SeoPage.objects.filter(page_key=page_key).first()
    if not seo_page:
        return {}
    return {
        "seo_title": seo_page.title,
        "seo_description": seo_page.description,
        "seo_image": seo_page.og_image.url if seo_page.og_image else None,
    }


def home(request):
    context = {
        "biography": Biography.objects.first(),
        "timeline_preview": TimelineEvent.objects.all()[:3],
        "gallery_preview": Photo.objects.all()[:6],
        "featured_memory": Memory.objects.filter(
            status=Memory.Status.APPROVED, featured=True
        ).first(),
        **_seo_context("home"),
    }
    return render(request, "pages/home.html", context)


def life(request):
    context = {
        "biography": Biography.objects.first(),
        "timeline": TimelineEvent.objects.all(),
        **_seo_context("life"),
    }
    return render(request, "pages/life.html", context)


def service(request):
    context = _seo_context("service")
    return render(request, "pages/service.html", context)


def photos(request):
    context = {
        "photos": Photo.objects.all(),
        **_seo_context("photos"),
    }
    return render(request, "pages/photos.html", context)


def videos(request):
    context = {
        "videos": Video.objects.all(),
        **_seo_context("videos"),
    }
    return render(request, "pages/videos.html", context)


def media(request):
    context = {
        "mentions": MediaMention.objects.all(),
        **_seo_context("media"),
    }
    return render(request, "pages/media.html", context)


def memories(request):
    context = {
        "memories": Memory.objects.filter(status=Memory.Status.APPROVED),
        **_seo_context("memories"),
    }
    return render(request, "pages/memories.html", context)


def styleguide(request):
    return render(request, "pages/styleguide.html", {})
