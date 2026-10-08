from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import translation

from apps.pages.models import ServicePage, ServiceQuote
from apps.pages.utils import make_service_quote_teaser
from apps.pages.validators import validate_service_quote


class ServiceQuotePresentationTests(TestCase):
    def test_labels_are_editable_and_translated(self):
        page = ServicePage.objects.create(
            is_published=True, quotes_description_uk="Опис цитат",
            quotes_description_en="Custom description", quote_less_label_en="Close quote",
            links_count_label_en="References",
        )
        ServiceQuote.objects.create(service_page=page, text_uk="Коротка цитата",
                                    text_en="Short quote", order=0)
        ServiceQuote.objects.create(service_page=page, text_uk="Довга цитата " * 50,
                                    text_en="Long quotation " * 50, order=1)
        response = self.client.get("/en/service/")
        self.assertContains(response, "Custom description")
        self.assertContains(response, 'data-less-label="Close quote"')
        self.assertContains(response, 'class="read-more"', count=1)
        self.assertContains(response, 'aria-hidden="true">“</span>', count=2)
        self.assertNotContains(response, "<figcaption>")
        with translation.override("uk"):
            page.refresh_from_db()
            self.assertEqual(page.quotes_description, "Опис цитат")

    def test_quote_length_and_whitespace(self):
        for invalid in ["", "   \n", "x" * 1501]:
            with self.assertRaises(ValidationError):
                validate_service_quote(invalid)
        validate_service_quote("x" * 1500)

    def test_teaser_breaks_at_word_boundary(self):
        text = "word " * 150
        teaser = make_service_quote_teaser(text)
        self.assertLessEqual(len(teaser), 500)
        self.assertTrue(teaser.endswith("word"))
        self.assertEqual(make_service_quote_teaser("Short"), "Short")

    def test_admin_quote_fields_enforce_limit_without_numeric_message(self):
        from django.contrib import admin
        from django.test import RequestFactory

        from apps.pages.admin import ServiceQuoteInline

        inline = ServiceQuoteInline(ServicePage, admin.site)
        for name in ["text_uk", "text_en"]:
            field = inline.formfield_for_dbfield(
                ServiceQuote._meta.get_field(name), RequestFactory().get("/admin/")
            )
            self.assertEqual(field.widget.attrs["maxlength"], 1500)
            with self.assertRaises(ValidationError) as error:
                field.clean("a" * 1501)
            self.assertNotIn("1500", str(error.exception))

    def test_short_and_empty_quotes(self):
        page = ServicePage.objects.create(is_published=True)
        response = self.client.get("/service/")
        self.assertNotContains(response, 'id="quotes"')
        ServiceQuote.objects.create(service_page=page, text="Коротка цитата")
        response = self.client.get("/service/")
        self.assertContains(response, "Коротка цитата")
        self.assertNotContains(response, 'class="read-more"')
