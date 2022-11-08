from django import template

register = template.Library()

@register.filter
def station_name(lst, i):
    return ''.join([x['namen']['lang'] for x in lst if x['UICCode'] == i])