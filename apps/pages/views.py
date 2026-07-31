from django.shortcuts import render
from django.views.decorators.http import require_safe


@require_safe
def home(request):
    return render(request, "pages/home.html")


@require_safe
def life(request):
    return render(request, "pages/life.html")


@require_safe
def service(request):
    return render(request, "pages/service.html")


@require_safe
def photos(request):
    return render(request, "pages/photos.html")


@require_safe
def videos(request):
    return render(request, "pages/videos.html")


@require_safe
def media(request):
    return render(request, "pages/media.html")


@require_safe
def memories(request):
    return render(request, "pages/memories.html")


@require_safe
def styleguide(request):
    return render(request, "pages/styleguide.html")