from django import template
import markdown as md
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(name='markdown')
def markdown_format(text):
    return mark_safe(md.markdown(text, extensions=['markdown.extensions.fenced_code', 'markdown.extensions.codehilite']))
