from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class StaticViewSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    i18n = True
    alternates = True
    x_default = True

    def items(self):
        return [
            "pages:home",
            "pages:life",
            "pages:service",
            "pages:photos",
            "pages:videos",
            "pages:memories",
        ]

    def location(self, item):
        return reverse(item)