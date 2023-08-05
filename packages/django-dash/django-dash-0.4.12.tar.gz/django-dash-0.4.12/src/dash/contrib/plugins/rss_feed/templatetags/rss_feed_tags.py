import datetime
from time import struct_time

from django import template

register = template.Library()

@register.filter
def convert_to_datetime(value):
    if isinstance(value, struct_time):
        converted = datetime.datetime(
            year=value.tm_year,
            month=value.tm_mon,
            day=value.tm_mday,
            hour=value.tm_hour,
            minute=value.tm_min,
            second=value.tm_sec
        )
    else:
        converted = value
    return converted
