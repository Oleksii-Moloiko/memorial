import logging
from urllib.parse import urlencode

from django.contrib import messages
from django.core.paginator import Paginator
from django.db import DatabaseError, transaction
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django_ratelimit.decorators import ratelimit

from apps.biography.models import Biography, TimelineEvent
from apps.core.models import SiteSettings
from apps.gallery.models import Photo
from apps.media_mentions.models import MediaMention
from apps.memories.forms import MemoryForm
from apps.memories.models import Memory, MemoryCategory
from apps.seo.models import SeoPage
from apps.videos.models import Video

from .constants import (
    MEMORY_TEASER_LIMIT,
    SERVICE_QUOTE_TEASER_LIMIT,
)
from .models import (
    HomePage,
    LifePage,
    PhotoPage,
    ServicePage,
    VideoPage,
)
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
    home_page = HomePage.objects.first() or HomePage()
    context = {
        "home_page": home_page,
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
    life_page = (
        LifePage.objects.select_related(
            "childhood_photo",
            "study_photo",
            "family_photo",
        ).first()
        or LifePage()
    )

    childhood_photo = life_page.childhood_photo
    study_photo = life_page.study_photo
    family_photo = life_page.family_photo

    if childhood_photo and not childhood_photo.is_published:
        childhood_photo = None

    if study_photo and not study_photo.is_published:
        study_photo = None

    if family_photo and not family_photo.is_published:
        family_photo = None

    context = {
        "life_page": life_page,
        "biography": Biography.objects.first(),
        "timeline": TimelineEvent.objects.all(),
        "childhood_photo": childhood_photo,
        "study_photo": study_photo,
        "family_photo": family_photo,
        **_seo_context("life"),
    }

    return render(
        request,
        "pages/life.html",
        context,
    )


def service(request):
    service_page = ServicePage.objects.filter(
        is_published=True,
    ).first()

    if service_page:
        quotes = list(service_page.quotes.all())

        mentions = MediaMention.objects.filter(
            is_published=True,
        )

        for quote in quotes:
            quote.is_long = len(quote.text) > SERVICE_QUOTE_TEASER_LIMIT

            quote.teaser = make_service_quote_teaser(quote.text)
    else:
        quotes = []
        mentions = MediaMention.objects.none()

    context = {
        "service_page": service_page,
        "quotes": quotes,
        "mentions": mentions,
        **_seo_context("service"),
    }

    return render(request, "pages/service.html", context)


def photos(request):
    photo_page = PhotoPage.objects.first() or PhotoPage()

    published_photos = Photo.objects.filter(is_published=True)

    category_counts = {
        "all": published_photos.count(),
    }

    for value, _label in Photo.Category.choices:
        category_counts[value] = published_photos.filter(
            category=value,
        ).count()

    settings = SiteSettings.load()
    photo_filters = [
        {
            "value": value,
            "label": getattr(settings, f"photo_category_{value}"),
            "count": category_counts[value],
        }
        for value, _label in Photo.Category.choices
    ]

    context = {
        "photo_page": photo_page,
        "photos": published_photos,
        "category_counts": category_counts,
        "photo_filters": photo_filters,
        **_seo_context("photos"),
    }

    return render(request, "pages/photos.html", context)


def videos(request):
    video_page = VideoPage.objects.first() or VideoPage()

    published_videos = Video.objects.filter(is_published=True)

    featured_video = published_videos.filter(is_featured=True).first()

    regular_videos = published_videos

    if featured_video:
        regular_videos = regular_videos.exclude(pk=featured_video.pk)

    context = {
        "video_page": video_page,
        "featured_video": featured_video,
        "featured_category_label": (
            getattr(SiteSettings.load(), f"video_category_{featured_video.category}", "")
            if featured_video else ""
        ),
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
        site_settings = SiteSettings.load()
        is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"
        form = MemoryForm(request.POST)
        error_message = site_settings.memories_error_message
        error_status = 400
        errors = {}

        if getattr(request, "limited", False):
            error_message = site_settings.memories_rate_limit_message
            error_status = 429
        elif form.is_valid():
            try:
                with transaction.atomic():
                    memory = form.save(commit=False)
                    memory.status = Memory.Status.PENDING
                    memory.featured = False
                    memory.save()
            except DatabaseError:
                logging.getLogger(__name__).exception("Failed to save a memory")
                error_status = 503
            else:
                success_message = site_settings.memories_success_message
                if is_ajax:
                    return JsonResponse({"success": True, "message": success_message})
                messages.success(request, success_message)
                return redirect("pages:memories")
        else:
            errors = form.errors.get_json_data()

        if is_ajax:
            return JsonResponse(
                {
                    "success": False,
                    "message": error_message,
                    "errors": errors,
                },
                status=error_status,
            )

        messages.error(request, error_message)
    else:
        form = MemoryForm()

    memories_queryset = (
        Memory.objects
        .filter(status=Memory.Status.APPROVED)
        .select_related("category")
        .order_by("-created_at", "-id")
    )

    selected_categories = sorted({
        int(value) for value in request.GET.get("category", "").split(",")
        if value.isascii() and value.isdigit() and len(value) <= 10
    })
    selected_categories = list(MemoryCategory.objects.filter(
        pk__in=selected_categories, is_active=True,
    ).values_list("pk", flat=True))
    if selected_categories:
        memories_queryset = memories_queryset.filter(category_id__in=selected_categories)

    paginator = Paginator(
        memories_queryset,
        12,
    )

    page_obj = paginator.get_page(
        request.GET.get("page")
    )

    for memory in page_obj.object_list:
        memory.is_long = (
                len(memory.text)
                > MEMORY_TEASER_LIMIT
        )
        memory.teaser = make_memory_teaser(
            memory.text
        )

    memory_categories = (
        MemoryCategory.objects
        .filter(is_active=True)
        .annotate(
            memories_count=Count(
                "memories",
                filter=Q(
                    memories__status=Memory.Status.APPROVED,
                ),
            ),
        )
        .filter(memories_count__gt=0)
        .order_by("sort_order", "id")
    )

    for category in memory_categories:
        category.selected = category.pk in selected_categories
        toggled = set(selected_categories) ^ {category.pk}
        category.filter_url = "?" + urlencode({"category": ",".join(map(str, sorted(toggled)))})

    page_links = []
    for number in paginator.get_elided_page_range(page_obj.number, on_each_side=1):
        page_links.append({
            "number": number,
            "ellipsis": number == paginator.ELLIPSIS,
        })

    context = {
        "page_links": page_links,
        "memories": page_obj.object_list,
        "page_obj": page_obj,
        "memory_categories": memory_categories,
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

def custom_404(request, exception):
    return render(
        request,
        "404.html",
        status=404,
    )