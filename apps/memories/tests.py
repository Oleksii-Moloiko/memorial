from django.contrib.admin.sites import AdminSite
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.utils.translation import override

from .admin import MemoryAdmin
from .forms import MemoryForm
from .models import Memory, MemoryCategory


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
        category = MemoryCategory.objects.create(name="Побратим")
        form = MemoryForm(
            data={
                "author_name": "  Іван  ",
                "category": category.pk,
                "text": "  Це достатньо довгий текст спогаду.  ",
                "consent": True,
            }
        )

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["author_name"], "Іван")
        self.assertEqual(form.cleaned_data["category"], category)
        self.assertEqual(
            form.cleaned_data["text"],
            "Це достатньо довгий текст спогаду.",
        )


class MemoriesPageTests(TestCase):
    def setUp(self):
        language = override("uk")
        language.__enter__()
        self.addCleanup(language.__exit__, None, None, None)
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

    def test_memories_are_paginated_by_twelve(self):
        for index in range(13):
            Memory.objects.create(
                author_name=f"Автор {index}",
                text=f"Опублікований спогад номер {index}.",
                status=Memory.Status.APPROVED,
            )

        response = self.client.get(self.url)

        self.assertEqual(
            len(response.context["memories"]),
            12,
        )

        self.assertTrue(
            response.context["page_obj"].has_next()
        )

    def test_second_page_contains_remaining_memories(self):
        for index in range(13):
            Memory.objects.create(
                author_name=f"Автор {index}",
                text=f"Опублікований спогад номер {index}.",
                status=Memory.Status.APPROVED,
            )

        response = self.client.get(
            self.url,
            {"page": 2},
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            len(response.context["memories"]),
            1,
        )

        self.assertEqual(
            response.context["page_obj"].number,
            2,
        )

    def test_memories_page_orders_newest_first(self):
        older = Memory.objects.create(
            author_name="Старіший",
            text="Старіший опублікований спогад.",
            status=Memory.Status.APPROVED,
        )

        newer = Memory.objects.create(
            author_name="Новіший",
            text="Новіший опублікований спогад.",
            status=Memory.Status.APPROVED,
        )

        response = self.client.get(self.url)

        memories = list(
            response.context["memories"]
        )

        self.assertEqual(
            memories[:2],
            [newer, older],
        )

class MemoryPaginationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = MemoryCategory.objects.create(name="Друзі")
        Memory.objects.bulk_create([
            Memory(author_name=f"Автор {index}", text="Світлий спогад. " * 80,
                   status=Memory.Status.APPROVED,
                   category=cls.category if index < 13 else None)
            for index in range(300)
        ])
        Memory.objects.create(author_name="Прихований", text="Неопублікований спогад.")

    def test_three_hundred_memories_are_bounded_and_navigable(self):
        response = self.client.get(reverse("pages:memories"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["page_obj"].paginator.count, 300)
        self.assertEqual(len(response.context["memories"]), 12)
        self.assertLessEqual(len(response.content), 150_000)
        self.assertContains(response, 'rel="next" href="?page=2"')
        self.assertNotContains(response, "Прихований")
        last = self.client.get(reverse("pages:memories"), {"page": 25})
        self.assertEqual(len(last.context["memories"]), 12)
        self.assertNotContains(last, 'rel="next"')
        self.assertTrue(last.context["page_obj"].has_previous())

    def test_filters_apply_before_pagination_and_survive_navigation(self):
        url = reverse("pages:memories")
        response = self.client.get(url, {"category": self.category.pk})
        self.assertEqual(response.context["page_obj"].paginator.count, 13)
        self.assertContains(response, f'?category={self.category.pk}&amp;page=2')
        second = self.client.get(url, {"category": self.category.pk, "page": 2})
        self.assertEqual(len(second.context["memories"]), 1)
        self.assertEqual(second.context["memories"][0].category_id, self.category.pk)

    def test_invalid_and_out_of_range_pages(self):
        for value, expected in [("bad", 1), ("0", 25), ("999", 25)]:
            with self.subTest(value=value):
                response = self.client.get(reverse("pages:memories"), {"page": value})
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.context["page_obj"].number, expected)

    def test_empty_page_and_english_navigation(self):
        response = self.client.get("/en/memories/")
        self.assertContains(response, "Memory pages")
        self.assertContains(response, "Next")
        Memory.objects.all().delete()
        response = self.client.get(reverse("pages:memories"))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'class="memories-pagination"')


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
