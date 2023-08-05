from django import template
from crm.date.models import Month


register = template.Library()


@register.simple_tag
def previous_month_name():
    return Month.previous()


@register.simple_tag
def current_month_name():
    return Month.current()


@register.simple_tag
def next_month_name():
    return Month.next()
