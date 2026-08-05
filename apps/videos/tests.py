import shutil
import tempfile
from types import SimpleNamespace

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import (
    Video,
    validate_video_extension,
    validate_video_size,
)


TEST_MEDIA_ROOT = tempfile.mkdtemp()


def create_test_video(name="test.mp4"):
    return SimpleUploadedFile(
        name=name,
        content=b"test video content",
        content_type="video/mp4",
    )


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class VideoModelTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEST_MEDIA_ROOT, ignore_errors=True)

    def test_video_string_representation(self):
        video = Video.objects.create(
            title="Інтерв’ю",
            video_file=create_test_video(),
        )

        self.assertEqual(str(video), "Інтерв’ю")

    def test_video_is_unpublished_by_default(self):
        video = Video.objects.create(
            title="Архівне відео",
            video_file=create_test_video(),
        )

        self.assertFalse(video.is_published)

    def test_video_is_not_featured_by_default(self):
        video = Video.objects.create(
            title="Архівне відео",
            video_file=create_test_video(),
        )

        self.assertFalse(video.is_featured)

    def test_default_category_is_other(self):
        video = Video.objects.create(
            title="Архівне відео",
            video_file=create_test_video(),
        )

        self.assertEqual(
            video.category,
            Video.Category.OTHER,
        )

    def test_videos_are_ordered_by_order_field(self):
        second_video = Video.objects.create(
            title="Друге відео",
            video_file=create_test_video("second.mp4"),
            order=20,
        )

        first_video = Video.objects.create(
            title="Перше відео",
            video_file=create_test_video("first.mp4"),
            order=10,
        )

        self.assertEqual(
            list(Video.objects.all()),
            [first_video, second_video],
        )


class VideoValidatorTests(TestCase):
    def test_mp4_extension_is_allowed(self):
        file = SimpleNamespace(
            name="video.mp4",
        )

        try:
            validate_video_extension(file)
        except ValidationError:
            self.fail("MP4-файл не повинен викликати ValidationError.")

    def test_webm_extension_is_allowed(self):
        file = SimpleNamespace(
            name="video.webm",
        )

        try:
            validate_video_extension(file)
        except ValidationError:
            self.fail("WebM-файл не повинен викликати ValidationError.")

    def test_mov_extension_is_allowed(self):
        file = SimpleNamespace(
            name="video.mov",
        )

        try:
            validate_video_extension(file)
        except ValidationError:
            self.fail("MOV-файл не повинен викликати ValidationError.")

    def test_extension_is_case_insensitive(self):
        file = SimpleNamespace(
            name="video.MP4",
        )

        try:
            validate_video_extension(file)
        except ValidationError:
            self.fail("Розширення у верхньому регістрі має підтримуватися.")

    def test_invalid_extension_is_rejected(self):
        file = SimpleNamespace(
            name="video.avi",
        )

        with self.assertRaisesMessage(
            ValidationError,
            "Дозволені формати відео: MP4, WebM або MOV.",
        ):
            validate_video_extension(file)

    def test_file_under_300_mb_is_allowed(self):
        file = SimpleNamespace(
            size=299 * 1024 * 1024,
        )

        try:
            validate_video_size(file)
        except ValidationError:
            self.fail("Файл до 300 MB не повинен викликати ValidationError.")

    def test_file_exactly_300_mb_is_allowed(self):
        file = SimpleNamespace(
            size=300 * 1024 * 1024,
        )

        try:
            validate_video_size(file)
        except ValidationError:
            self.fail("Файл розміром 300 MB має бути дозволений.")

    def test_file_over_300_mb_is_rejected(self):
        file = SimpleNamespace(
            size=(300 * 1024 * 1024) + 1,
        )

        with self.assertRaisesMessage(
            ValidationError,
            "Розмір відео не повинен перевищувати 300 MB.",
        ):
            validate_video_size(file)


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class VideosPageTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEST_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.url = reverse("pages:videos")

    def test_videos_page_is_available(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "pages/videos.html",
        )

    def test_published_video_is_visible(self):
        video = Video.objects.create(
            title="Опубліковане відео",
            video_file=create_test_video(),
            is_published=True,
        )

        response = self.client.get(self.url)

        self.assertContains(response, video.title)
        self.assertContains(response, video.video_file.url)

    def test_unpublished_video_is_hidden(self):
        video = Video.objects.create(
            title="Неопубліковане відео",
            video_file=create_test_video(),
            is_published=False,
        )

        response = self.client.get(self.url)

        self.assertNotContains(response, video.title)

    def test_featured_video_is_displayed_in_featured_section(self):
        video = Video.objects.create(
            title="Рекомендоване відео",
            video_file=create_test_video(),
            description="Опис рекомендованого відео.",
            is_featured=True,
            is_published=True,
        )

        response = self.client.get(self.url)

        self.assertEqual(
            response.context["featured_video"],
            video,
        )
        self.assertContains(
            response,
            "Рекомендоване відео",
        )
        self.assertContains(
            response,
            video.description,
        )

    def test_featured_video_is_excluded_from_regular_videos(self):
        featured_video = Video.objects.create(
            title="Головне відео",
            video_file=create_test_video("featured.mp4"),
            is_featured=True,
            is_published=True,
        )

        regular_video = Video.objects.create(
            title="Звичайне відео",
            video_file=create_test_video("regular.mp4"),
            is_published=True,
        )

        response = self.client.get(self.url)

        self.assertEqual(
            response.context["featured_video"],
            featured_video,
        )

        self.assertIn(
            regular_video,
            response.context["videos"],
        )

        self.assertNotIn(
            featured_video,
            response.context["videos"],
        )

    def test_unpublished_featured_video_is_not_displayed(self):
        Video.objects.create(
            title="Приховане рекомендоване відео",
            video_file=create_test_video(),
            is_featured=True,
            is_published=False,
        )

        response = self.client.get(self.url)

        self.assertIsNone(
            response.context["featured_video"],
        )

    def test_video_metadata_is_displayed(self):
        video = Video.objects.create(
            title="Відео зі служби",
            video_file=create_test_video(),
            category=Video.Category.SERVICE,
            recorded_at="2023",
            duration="03:42",
            transcript="Текстова розшифровка відео.",
            is_featured=True,
            is_published=True,
        )

        response = self.client.get(self.url)

        self.assertContains(response, "2023")
        self.assertContains(response, "03:42")
        self.assertContains(response, "Служба")
        self.assertContains(
            response,
            "Текстова розшифровка відео.",
        )

    def test_empty_state_is_displayed(self):
        response = self.client.get(self.url)

        self.assertContains(
            response,
            "Відеоархів ще наповнюється",
        )