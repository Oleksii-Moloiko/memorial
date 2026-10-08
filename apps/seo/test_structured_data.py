from datetime import UTC, datetime
from types import SimpleNamespace

from django.test import RequestFactory, SimpleTestCase, override_settings
from django.urls import resolve

from apps.seo.structured_data import (
    build_breadcrumbs,
    build_image_gallery,
    build_videos,
    iso_duration,
)
from apps.seo.templatetags.structured_data import json_ld


def make_video(**kwargs):
    defaults = {
        "title": "Інтерв'ю",
        "description": "<p>Опис</p>",
        "thumbnail": SimpleNamespace(url="/media/t.jpg"),
        "responsive_thumbnail": None,
        "created_at": datetime(2026, 9, 1, tzinfo=UTC),
        "video_file": SimpleNamespace(url="https://cdn.example.com/v.mp4"),
        "duration": "03:42",
        "transcript": "",
    }
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


@override_settings(SITE_URL="https://example.com")
class StructuredDataTests(SimpleTestCase):
    def setUp(self):
        self.request = RequestFactory().get("/photos/")

    def test_iso_duration(self):
        self.assertEqual(iso_duration("03:42"), "PT0H3M42S")
        self.assertEqual(iso_duration("1:02:03"), "PT1H2M3S")
        self.assertIsNone(iso_duration("близько 5 хв"))
        self.assertIsNone(iso_duration(""))

    def test_image_gallery(self):
        photos = [
            SimpleNamespace(
                image=SimpleNamespace(url="/media/a.jpg"),
                caption="Підпис",
            ),
            SimpleNamespace(image=None, caption=""),
        ]
        data = build_image_gallery(
            self.request, photos, name="Фото", description="Опис"
        )
        self.assertEqual(data["@type"], "ImageGallery")
        self.assertEqual(data["url"], "https://example.com/photos/")
        self.assertEqual(data["description"], "Опис")
        self.assertEqual(len(data["image"]), 1)
        self.assertEqual(
            data["image"][0]["contentUrl"], "https://example.com/media/a.jpg"
        )
        self.assertEqual(data["image"][0]["caption"], "Підпис")
        self.assertEqual(data["about"]["@id"], "https://example.com/#person")

    def test_image_gallery_without_caption_or_description(self):
        photos = [SimpleNamespace(image=SimpleNamespace(url="/m/b.jpg"), caption="")]
        data = build_image_gallery(self.request, photos, name="Фото")
        self.assertNotIn("caption", data["image"][0])
        self.assertNotIn("description", data)

    def test_image_gallery_empty(self):
        self.assertIsNone(build_image_gallery(self.request, [], name="Фото"))

    def test_videos(self):
        data = build_videos(self.request, [make_video(), make_video(thumbnail=None)])
        self.assertEqual(len(data["@graph"]), 1)
        item = data["@graph"][0]
        self.assertEqual(item["@type"], "VideoObject")
        self.assertEqual(item["description"], "Опис")
        self.assertEqual(item["thumbnailUrl"], "https://example.com/media/t.jpg")
        self.assertEqual(item["contentUrl"], "https://cdn.example.com/v.mp4")
        self.assertEqual(item["uploadDate"], "2026-09-01T00:00:00+00:00")
        self.assertEqual(item["duration"], "PT0H3M42S")
        self.assertNotIn("transcript", item)

    def test_video_uses_responsive_thumbnail_and_transcript(self):
        data = build_videos(
            self.request,
            [
                make_video(
                    responsive_thumbnail={"src": "/media/t-800.jpg"},
                    description="",
                    duration="",
                    transcript="Текст",
                )
            ],
        )
        item = data["@graph"][0]
        self.assertEqual(item["thumbnailUrl"], "https://example.com/media/t-800.jpg")
        self.assertEqual(item["description"], "Інтерв'ю")
        self.assertEqual(item["transcript"], "Текст")
        self.assertNotIn("duration", item)

    def test_videos_empty(self):
        self.assertIsNone(build_videos(self.request, [make_video(thumbnail=None)]))

    def test_breadcrumbs(self):
        request = RequestFactory().get("/life/")
        request.resolver_match = resolve("/life/")
        site_settings = SimpleNamespace(home_title="Головна", life_title="Життя")
        data = build_breadcrumbs(request, site_settings)
        items = data["itemListElement"]
        self.assertEqual([i["name"] for i in items], ["Головна", "Життя"])
        self.assertEqual(items[1]["item"], "https://example.com/life/")

    def test_breadcrumbs_absent_on_home(self):
        request = RequestFactory().get("/")
        request.resolver_match = resolve("/")
        site_settings = SimpleNamespace(home_title="Головна")
        self.assertIsNone(build_breadcrumbs(request, site_settings))

    def test_json_ld_escapes_script_tag(self):
        html = json_ld({"name": "</script><b>"})
        self.assertNotIn("</script><b>", html)
        self.assertIn("\\u003C/script\\u003E", html)

    def test_json_ld_empty(self):
        self.assertEqual(json_ld(None), "")
