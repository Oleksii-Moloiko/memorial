from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db import DatabaseError
from django.test import TestCase, override_settings
from django.urls import reverse

from apps.core.models import SiteSettings

from .models import Memory


@override_settings(RATELIMIT_ENABLE=False)
class MemorySubmissionMessageTests(TestCase):
    def setUp(self):
        cache.clear()
        self.addCleanup(cache.clear)
        self.settings = SiteSettings.load()
        self.settings.memories_success_message = "Дякуємо за ваші слова!"
        self.settings.memories_error_message = "Помилка — повторіть спробу."
        self.settings.memories_rate_limit_message = (
            "Зачекайте перед наступним надсиланням."
        )
        self.settings.memories_submit_button_label = "Поділитися"
        self.settings.memories_success_message_en = "Thank you for your memory!"
        self.settings.memories_error_message_en = "Please try again."
        self.settings.memories_submit_button_label_en = "Share a memory"
        self.settings.save()
        self.url = reverse("pages:memories")
        self.data = {
            "author_name": "Іван",
            "author_role": "Друг",
            "text": "Це достатньо довгий текст спогаду про людину.",
            "consent": "on",
        }

    def post_ajax(self, data=None, url=None):
        return self.client.post(
            url or self.url,
            data=self.data if data is None else data,
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

    def test_success_uses_settings_and_creates_pending_memory(self):
        response = self.post_ajax()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "success": True,
                "message": self.settings.memories_success_message,
            },
        )
        memory = Memory.objects.get()
        self.assertEqual(memory.status, Memory.Status.PENDING)
        self.assertFalse(memory.featured)

    def test_regular_success_uses_settings(self):
        response = self.client.post(self.url, self.data, follow=True)
        self.assertContains(response, self.settings.memories_success_message)

    def test_validation_includes_custom_toast_and_field_errors(self):
        response = self.post_ajax({**self.data, "consent": ""})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()["message"], self.settings.memories_error_message
        )
        self.assertIn("consent", response.json()["errors"])
        self.assertFalse(Memory.objects.exists())

    def test_regular_validation_preserves_fields(self):
        response = self.client.post(self.url, {**self.data, "consent": ""})
        self.assertContains(response, self.settings.memories_error_message)
        self.assertContains(response, self.data["text"])
        self.assertEqual(response.context["form"]["author_name"].value(), "Іван")

    @override_settings(RATELIMIT_ENABLE=True)
    @patch("django_ratelimit.decorators.is_ratelimited", return_value=True)
    def test_rate_limit_uses_settings_and_preserves_regular_form(self, limited):
        response = self.post_ajax()
        self.assertEqual(response.status_code, 429)
        self.assertEqual(
            response.json()["message"], self.settings.memories_rate_limit_message
        )
        response = self.client.post(self.url, self.data)
        self.assertContains(response, self.settings.memories_rate_limit_message)
        self.assertContains(response, self.data["text"])
        self.assertTrue(response.context["form"]["consent"].value())
        self.assertFalse(Memory.objects.exists())

    @patch("apps.pages.views.Memory.save", side_effect=DatabaseError("unavailable"))
    def test_save_failure_uses_custom_message_and_preserves_regular_form(self, save):
        with self.assertLogs("apps.pages.views", level="ERROR"):
            response = self.post_ajax()
        self.assertEqual(response.status_code, 503)
        self.assertEqual(
            response.json()["message"], self.settings.memories_error_message
        )
        with self.assertLogs("apps.pages.views", level="ERROR"):
            response = self.client.post(self.url, self.data)
        self.assertContains(response, self.settings.memories_error_message)
        self.assertContains(response, self.data["text"])
        self.assertFalse(Memory.objects.exists())

    def test_template_escapes_custom_messages_and_button(self):
        self.settings.memories_error_message = 'Помилка "<script>alert(1)</script>"'
        self.settings.save()
        response = self.client.get(self.url)
        self.assertContains(
            response,
            'data-error-message="Помилка &quot;&lt;script&gt;alert(1)&lt;/script&gt;&quot;"',
        )
        self.assertContains(response, self.settings.memories_submit_button_label)

    def test_english_messages_and_button(self):
        response = self.client.get("/en/memories/")
        self.assertContains(response, "Share a memory")
        self.assertContains(response, 'data-error-message="Please try again."')
        response = self.post_ajax(url="/en/memories/")
        self.assertEqual(response.json()["message"], "Thank you for your memory!")
        response = self.post_ajax({"consent": ""}, url="/en/memories/")
        self.assertEqual(response.json()["message"], "Please try again.")

    def test_admin_exposes_message_and_button_translations(self):
        user = get_user_model().objects.create_superuser(
            username="admin", password="test"
        )
        self.client.force_login(user)
        response = self.client.get(reverse("admin:core_sitesettings_change", args=[1]))
        self.assertEqual(response.status_code, 200)
        for field in (
            "success_message",
            "error_message",
            "rate_limit_message",
            "submit_button_label",
        ):
            for language in ("uk", "en"):
                self.assertContains(response, f'name="memories_{field}_{language}"')
