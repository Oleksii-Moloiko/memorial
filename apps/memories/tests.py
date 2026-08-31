from django.contrib.admin.sites import AdminSite
from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.middleware import SessionMiddleware

from .forms import MemoryForm
from .models import Memory
from .admin import MemoryAdmin

class MemoryModelTests(TestCase):
    def test_memory_string_representation(self):
        memory = Memory.objects.create(
            author_name="Іван",
            text="Це добрий і щирий спогад про людину.",
        )

        self.assertEqual(
            str(memory),
            "Іван: Це добрий і щирий спогад про людину.",
        )

    def test_memory_has_pending_status_by_default(self):
        memory = Memory.objects.create(
            author_name="Іван",
            text="Це достатньо довгий текст спогаду.",
        )

        self.assertEqual(
            memory.status,
            Memory.Status.PENDING,
        )

    def test_memories_are_ordered_from_newest(self):
        first_memory = Memory.objects.create(
            author_name="Перший автор",
            text="Перший достатньо довгий спогад.",
        )

        second_memory = Memory.objects.create(
            author_name="Другий автор",
            text="Другий достатньо довгий спогад.",
        )

        self.assertEqual(
            list(Memory.objects.all()),
            [second_memory, first_memory],
        )


class MemoryFormTests(TestCase):
    def test_valid_form(self):
        form = MemoryForm(
            data={
                "author_name": "Іван",
                "author_role": "Побратим",
                "text": "Це щирий і достатньо довгий спогад.",
                "consent": True,
            }
        )

        self.assertTrue(form.is_valid())

    def test_consent_is_required(self):
        form = MemoryForm(
            data={
                "author_name": "Іван",
                "author_role": "Побратим",
                "text": "Це щирий і достатньо довгий спогад.",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("consent", form.errors)

    def test_author_name_must_have_at_least_two_characters(self):
        form = MemoryForm(
            data={
                "author_name": "І",
                "author_role": "Побратим",
                "text": "Це щирий і достатньо довгий спогад.",
                "consent": True,
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("author_name", form.errors)

    def test_text_must_have_at_least_ten_characters(self):
        form = MemoryForm(
            data={
                "author_name": "Іван",
                "author_role": "Побратим",
                "text": "Коротко",
                "consent": True,
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("text", form.errors)

    def test_form_trims_whitespace(self):
        form = MemoryForm(
            data={
                "author_name": "  Іван  ",
                "author_role": "  Побратим  ",
                "text": "  Це достатньо довгий текст спогаду.  ",
                "consent": True,
            }
        )

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["author_name"], "Іван")
        self.assertEqual(form.cleaned_data["author_role"], "Побратим")
        self.assertEqual(
            form.cleaned_data["text"],
            "Це достатньо довгий текст спогаду.",
        )


class MemoriesPageTests(TestCase):
    def setUp(self):
        self.url = reverse("pages:memories")

    def test_page_is_available(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "pages/memories.html",
        )

    def test_approved_memory_is_visible(self):
        memory = Memory.objects.create(
            author_name="Іван",
            author_role="Побратим",
            text="Опублікований спогад про важливу людину.",
            status=Memory.Status.APPROVED,
        )

        response = self.client.get(self.url)

        self.assertContains(response, memory.author_name)
        self.assertContains(response, memory.text)

    def test_pending_memory_is_hidden(self):
        memory = Memory.objects.create(
            author_name="Іван",
            text="Цей спогад ще очікує на модерацію.",
            status=Memory.Status.PENDING,
        )

        response = self.client.get(self.url)

        self.assertNotContains(response, memory.text)

    def test_rejected_memory_is_hidden(self):
        memory = Memory.objects.create(
            author_name="Іван",
            text="Цей спогад було відхилено модератором.",
            status=Memory.Status.REJECTED,
        )

        response = self.client.get(self.url)

        self.assertNotContains(response, memory.text)

    def test_valid_form_creates_pending_memory(self):
        response = self.client.post(
            self.url,
            data={
                "author_name": "  Іван  ",
                "author_role": "Побратим",
                "text": "Це новий спогад, відправлений через форму.",
                "consent": True,
            },
        )

        self.assertRedirects(
            response,
            self.url,
        )

        memory = Memory.objects.get()

        self.assertEqual(memory.author_name, "Іван")
        self.assertEqual(memory.status, Memory.Status.PENDING)
        self.assertFalse(memory.featured)

    def test_invalid_form_does_not_create_memory(self):
        response = self.client.post(
            self.url,
            data={
                "author_name": "І",
                "author_role": "Побратим",
                "text": "Коротко",
                "consent": False,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Memory.objects.count(), 0)
        self.assertContains(
            response,
            "Вкажіть ім’я або підпис щонайменше з двох символів.",
        )

    def test_success_message_is_added_after_submission(self):
        response = self.client.post(
            self.url,
            data={
                "author_name": "Іван",
                "author_role": "Побратим",
                "text": "Це новий достатньо довгий спогад.",
                "consent": True,
            },
            follow=True,
        )

        self.assertContains(
            response,
            "Дякуємо. Ваш спогад надіслано на модерацію.",
        )

class MemoryAdminStatusTests(TestCase):
    def setUp(self):
        self.admin = MemoryAdmin(Memory, AdminSite())
        self.factory = RequestFactory()

    def test_rejected_featured_memory_is_unfeatured(self):
        memory = Memory.objects.create(
            author_name="Іван",
            text="Достатньо довгий текст спогаду.",
            status=Memory.Status.APPROVED,
            featured=True,
        )

        request = self.factory.post("/admin/")

        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)
        request.session.save()

        request._messages = FallbackStorage(request)

        self.admin._update_status(
            request,
            Memory.objects.filter(pk=memory.pk),
            Memory.Status.REJECTED,
        )

        memory.refresh_from_db()

        self.assertEqual(
            memory.status,
            Memory.Status.REJECTED,
        )
        self.assertFalse(memory.featured)