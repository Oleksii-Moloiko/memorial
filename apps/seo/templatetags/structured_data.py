import json

from django import template
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from apps.seo.structured_data import build_breadcrumbs

register = template.Library()


@register.simple_tag
def json_ld(data):
    if not data:
        return ""

    serialized = json.dumps(
        data,
        cls=DjangoJSONEncoder,
        ensure_ascii=False,
    ).translate(
        {
            ord("<"): "\\u003C",
            ord(">"): "\\u003E",
            ord("&"): "\\u0026",
        }
    )

    return format_html(
        '<script type="application/ld+json">{}</script>',
        mark_safe(serialized),
    )


@register.simple_tag(takes_context=True)
def breadcrumbs_json_ld(context):
    request = context.get("request")
    if request is None:
        return ""

    return json_ld(build_breadcrumbs(request, context.get("site_settings")))
