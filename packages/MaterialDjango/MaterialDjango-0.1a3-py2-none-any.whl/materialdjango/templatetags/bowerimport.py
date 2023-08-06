from django import template
from django.conf import settings

register = template.Library()

@register.assignment_tag(takes_context=False)
def bowerimport(parser, token):
    pass

