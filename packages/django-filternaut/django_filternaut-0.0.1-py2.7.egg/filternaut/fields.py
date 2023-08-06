from django.forms import DateTimeField
from django.utils.dateparse import parse_datetime


class DateTimeZoneField(DateTimeField):

    def clean(self, value):
        parent = super(DateTimeZoneField, self)
        return parent.clean(parse_datetime(value))
