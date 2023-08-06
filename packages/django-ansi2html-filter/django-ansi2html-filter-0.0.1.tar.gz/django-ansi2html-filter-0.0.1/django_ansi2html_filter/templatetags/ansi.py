from django import template
from django.utils.html import escape, mark_safe
import ansi2html
from ansi2html.style import get_styles

register = template.Library()
conv = ansi2html.Ansi2HTMLConverter()


@register.filter(name='ansi2html')
def ansi(value):
    return mark_safe(conv.convert(escape(value), full=False))


@register.simple_tag(name='ansi2html_styles')
def ansi_styles(scheme='solarized', dark_bg=True):
    return "\n".join(map(str, get_styles(dark_bg, scheme)[1:]))
