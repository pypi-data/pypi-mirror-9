from django.template import Library


register = Library()


@register.tag
def simple_thing(value):
    return value
