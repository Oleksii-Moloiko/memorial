from django.shortcuts import render

from apps.biography.models import Biography
from apps.gallery.models import Photo
from apps.media_mentions.models import MediaMention
from apps.memories.models import Memory
from apps.seo.models import SeoPage
from apps.videos.models import Video


def _seo(page_key):
    """SEO-метадані для сторінки, або None якщо ще не заповнені в адмінці —
    includes/seo_meta.html підставляє дефолти сам."""
    return SeoPage.objects.filter(page_key=page_key).first()


def home(request):
    context = {
        "biography": Biography.objects.first(),
        "photos": Photo.objects.all()[:6],
        "seo_page": _seo("home"),
    }
    return render(request, "pages/home.html", context)


def life(request):
    context = {
        "biography": Biography.objects.first(),
        "seo_page": _seo("life"),
    }
    return render(request, "pages/life.html", context)


def service(request):
    context = {
        "seo_page": _seo("service"),
    }
    return render(request, "pages/service.html", context)


def photos(request):
    context = {
        "photos": Photo.objects.all(),
        "seo_page": _seo("photos"),
    }
    return render(request, "pages/photos.html", context)


def videos(request):
    context = {
        "videos": Video.objects.all(),
        "seo_page": _seo("videos"),
    }
    return render(request, "pages/videos.html", context)


def media(request):
    context = {
        "mentions": MediaMention.objects.all(),
        "seo_page": _seo("media"),
    }
    return render(request, "pages/media.html", context)


def memories(request):
    context = {
        "memories": Memory.objects.filter(status=Memory.Status.APPROVED),
        "seo_page": _seo("memories"),
    }
    return render(request, "pages/memories.html", context)
