from importlib import import_module

from django.contrib.admin.sites import AdminSite
from django.db import connection
from django.test import RequestFactory, TestCase, override_settings
from django.utils.translation import override

from .admin import MemoryAdmin
from .forms import MemoryForm
from .models import Memory, MemoryCategory


@override_settings(RATELIMIT_ENABLE=False)
class MemoryReworkTests(TestCase):
    def setUp(self):
        self.category = MemoryCategory.objects.create(
            name_uk="Родина", name_en="Family"
        )

    def test_submission_length_boundary_and_category(self):
        for size, valid in ((15000, True), (15001, False)):
            with self.subTest(size=size), override("uk"):
                form = MemoryForm(
                    data={
                        "author_name": "Автор",
                        "category": self.category.pk,
                        "text": "а" * size,
                        "consent": True,
                    }
                )
                self.assertEqual(form.is_valid(), valid)
                if valid:
                    self.assertEqual(form.save().category, self.category)
                else:
                    self.assertIn("Досягнуто ліміт в 15 000", form.errors["text"][0])

    def test_admin_category_and_independent_translations(self):
        admin = MemoryAdmin(Memory, AdminSite())
        fields = admin.get_form(RequestFactory().get("/admin/")).base_fields
        self.assertTrue({"category", "text_uk", "text_en"}.issubset(fields))
        memory = Memory.objects.create(
            author_name="Автор", text_uk="Український спогад", text_en="English memory"
        )
        with override("en"):
            memory.text = "Updated English memory"
            memory.save()
        memory.refresh_from_db()
        self.assertEqual(memory.text_uk, "Український спогад")
        self.assertEqual(memory.text_en, "Updated English memory")

    def test_renamed_categories_used_in_form_and_filters(self):
        Memory.objects.create(
            author_name="Автор",
            text="Достатньо довгий спогад",
            category=self.category,
            status="approved",
        )
        self.category.name_en = "Relatives"
        self.category.save()
        response = self.client.get("/en/memories/")
        self.assertContains(response, "Relatives", count=3)
        self.assertContains(response, f'data-memory-filter="{self.category.pk}"')
        self.assertContains(response, "Choose an option")
        self.assertNotContains(response, "Досягнуто ліміт")

    def test_english_long_memory_button(self):
        Memory.objects.create(
            author_name="Автор", text_en="A long memory. " * 50, status="approved"
        )
        response = self.client.get("/en/memories/")
        self.assertContains(response, "Read more")
        self.assertNotContains(response, "Дивитись більше")

    def test_migration_preserves_legacy_text_without_overwriting_translations(self):
        legacy = Memory.objects.create(author_name="Legacy", text="Original memory")
        translated = Memory.objects.create(
            author_name="Translated",
            text_uk="Власний переклад",
            text_en="Existing translation",
        )
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE memories_memory SET text_uk = NULL, text_en = NULL WHERE id = %s",
                [legacy.pk],
            )
        migrate = import_module(
            "apps.memories.migrations.0007_preserve_existing_memory_text"
        ).preserve_existing_text
        # Historical models do not use modeltranslation's query rewriting.
        from django.db.migrations.executor import MigrationExecutor

        historical = MigrationExecutor(connection).loader.project_state().apps
        from types import SimpleNamespace

        migrate(historical, SimpleNamespace(connection=connection))
        legacy.refresh_from_db()
        translated.refresh_from_db()
        self.assertEqual(legacy.text_uk, "Original memory")
        self.assertEqual(translated.text_uk, "Власний переклад")
        self.assertEqual(translated.text_en, "Existing translation")
