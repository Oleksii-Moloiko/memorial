from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django_ratelimit.decorators import ratelimit

from apps.biography.models import Biography, TimelineEvent
from apps.gallery.models import Photo
from apps.media_mentions.models import MediaMention
from apps.memories.forms import MemoryForm
from apps.memories.models import Memory
from apps.seo.models import SeoPage
from apps.videos.models import Video

from .constants import (
    MEMORY_TEASER_LIMIT,
    SERVICE_QUOTE_TEASER_LIMIT,
)
from .models import ServicePage
from .utils import (
    make_memory_teaser,
    make_service_quote_teaser,
)


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

        "timeline_preview": TimelineEvent.objects.all(),

        "gallery_preview": Photo.objects.filter(
            is_published=True,
        )[:4],

        "featured_memory": Memory.objects.filter(
            status=Memory.Status.APPROVED,
            featured=True,
        ).first(),

        "featured_video": Video.objects.filter(
            is_published=True,
            is_featured=True,
        ).first(),

        "featured_mention": MediaMention.objects.filter(
            is_published=True,
            is_featured=True,
        ).first(),

        **_seo_context("home"),
    }

    return render(
        request,
        "pages/home.html",
        context,
    )


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
    service_page = ServicePage.objects.filter(
        is_published=True,
    ).first()

    mentions = MediaMention.objects.filter(
        is_published=True,
    )

    if service_page:
        quotes = list(service_page.quotes.all())

        for quote in quotes:
            quote.is_long = (
                len(quote.text) > SERVICE_QUOTE_TEASER_LIMIT
            )
            quote.teaser = make_service_quote_teaser(
                quote.text
            )
    else:
        quotes = []

    context = {
        "service_page": service_page,
        "quotes": quotes,
        "mentions": mentions,
        **_seo_context("service"),
    }

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
    return redirect("/service/#links")

@ratelimit(
    key="ip",
    rate="3/h",
    method="POST",
    block=False,
)
def memories(request):
    if request.method == "POST":
        is_ajax = (
                request.headers.get("X-Requested-With")
                == "XMLHttpRequest"
        )

        if getattr(request, "limited", False):
            limit_message = (
                "Ви надіслали кілька спогадів за короткий час. "
                "Спробуйте, будь ласка, пізніше."
            )

            if is_ajax:
                return JsonResponse(
                    {
                        "success": False,
                        "message": limit_message,
                    },
                    status=429,
                )

            messages.error(
                request,
                limit_message,
            )

            return redirect("pages:memories")

        form = MemoryForm(request.POST)

        if form.is_valid():
            memory = form.save(commit=False)
            memory.status = Memory.Status.PENDING
            memory.featured = False
            memory.save()

            success_message = (
                "Дякуємо. Ваш спогад надіслано на модерацію."
            )

            if is_ajax:
                return JsonResponse({
                    "success": True,
                    "message": success_message,
                })

            messages.success(
                request,
                success_message,
            )

            return redirect("pages:memories")

        if is_ajax:
            return JsonResponse(
                {
                    "success": False,
                    "errors": form.errors.get_json_data(),
                },
                status=400,
            )

        else:
            messages.error(
                request,
                "Щось пішло не так. Перевірте дані у формі та спробуйте ще раз.",
            )

    else:
        form = MemoryForm()

    memories_queryset = Memory.objects.filter(
        status=Memory.Status.APPROVED,
    )

    featured_memory = memories_queryset.filter(
        featured=True,
    ).first()

    regular_memories = list(
        memories_queryset.filter(
            featured=False,
        )
    )

    if featured_memory and regular_memories:
        memories_list = [
            regular_memories[0],
            featured_memory,
            *regular_memories[1:],
        ]
    elif featured_memory:
        memories_list = [featured_memory]
    else:
        memories_list = regular_memories

    for memory in memories_list:
        memory.is_long = len(memory.text) > MEMORY_TEASER_LIMIT
        memory.teaser = make_memory_teaser(memory.text)



    context = {
        "memories": memories_list,
        "form": form,

        **_seo_context("memories"),
    }

    return render(
        request,
        "pages/memories.html",
        context,
    )


def styleguide(request):
    return render(request, "pages/styleguide.html", {})