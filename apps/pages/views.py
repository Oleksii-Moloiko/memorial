from django.contrib import messages
from django.shortcuts import redirect, render

from apps.biography.models import Biography, TimelineEvent
from apps.gallery.models import Photo
from apps.media_mentions.models import MediaMention
from apps.memories.forms import MemoryForm
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
        "gallery_preview": Photo.objects.filter(is_published=True)[:6],
        "featured_memory": Memory.objects.filter(
            status=Memory.Status.APPROVED, featured=True
        ).first(),
        **_seo_context("home"),
    }
    return render(request, "pages/home.html", context)


def life(request):
    family_photos = list(
        Photo.objects.filter(
            category=Photo.Category.FAMILY, is_published=True
        )[:2]
    )
    study_photo = Photo.objects.filter(
        category=Photo.Category.STUDY, is_published=True
    ).first()

    context = {
        "biography": Biography.objects.first(),
        "timeline": TimelineEvent.objects.all(),
        "childhood_photo": family_photos[0] if len(family_photos) > 0 else None,
        "family_photo": family_photos[1] if len(family_photos) > 1 else None,
        "study_photo": study_photo,
        **_seo_context("life"),
    }
    return render(request, "pages/life.html", context)


def service(request):
    context = _seo_context("service")
    return render(request, "pages/service.html", context)


def photos(request):
    published_photos = Photo.objects.filter(is_published=True)

    category_counts = {
        "all": published_photos.count(),
        "family": published_photos.filter(category=Photo.Category.FAMILY).count(),
        "study": published_photos.filter(category=Photo.Category.STUDY).count(),
        "service": published_photos.filter(category=Photo.Category.SERVICE).count(),
        "memory": published_photos.filter(category=Photo.Category.MEMORY).count(),
    }

    context = {
        "photos": published_photos,
        "category_counts": category_counts,
        **_seo_context("photos"),
    }

    return render(request, "pages/photos.html", context)


def videos(request):
    published_videos = Video.objects.filter(is_published=True)

    featured_video = published_videos.filter(is_featured=True).first()

    regular_videos = published_videos

    if featured_video:
        regular_videos = regular_videos.exclude(pk=featured_video.pk)

    context = {
        "featured_video": featured_video,
        "videos": regular_videos,
        **_seo_context("videos"),
    }

    return render(
        request,
        "pages/videos.html",
        context,
    )


def media(request):
    context = {
        "mentions": MediaMention.objects.all(),
        **_seo_context("media"),
    }
    return render(request, "pages/media.html", context)


def memories(request):
    if request.method == "POST":
        form = MemoryForm(request.POST)

        if form.is_valid():
            memory = form.save(commit=False)
            memory.status = Memory.Status.PENDING
            memory.featured = False
            memory.save()

            messages.success(
                request,
                "Дякуємо. Ваш спогад надіслано на модерацію.",
            )

            return redirect("pages:memories")
    else:
        form = MemoryForm()

    context = {
        "memories": Memory.objects.filter(status=Memory.Status.APPROVED),
        "form": form,
        **_seo_context("memories"),
    }

    return render(request, "pages/memories.html", context)


def styleguide(request):
    return render(request, "pages/styleguide.html", {})