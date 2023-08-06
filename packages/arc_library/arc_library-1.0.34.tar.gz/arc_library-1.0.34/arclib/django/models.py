# -*- coding: utf-8 -*-
from django.utils.six import with_metaclass
from django.db import models
from timedelta.fields import TimedeltaField

def imageinfo(instance, url=None):
    dict = {
        'has_image': True if instance else False,
        'width': instance.width if instance else '',
        'height': instance.height if instance else '',
        'url': instance.url if instance else url,
    }
    if not instance and url is None:
        dict['url'] = ''
    return dict

class ArcImageField(with_metaclass(models.SubfieldBase, models.ImageField)):
    def __init__(self, *args, **kwargs):
        super(ArcImageField, self).__init__(*args, **kwargs)

    def imageinfo(self, url=None):
        return imageinfo(self, url)

class ArcTimedeltaField(TimedeltaField):
    def __init__(self, *args, **kwargs):
        super(ArcTimedeltaField, self).__init__(*args, **kwargs)

    def years(self):
        seconds = self.total_seconds()
        years = seconds / (3600 * 24 * 365)
        return years

    def days(self):
        seconds = self.total_seconds()
        years = self.years()
        remain_seconds = seconds - (years * 3600 * 24 * 365)
        days = remain_seconds / (3600 * 24)
        return days

    def hours(self):
        seconds = self.total_seconds()
        years = self.years()
        days = self.days()
        remain_seconds = seconds - (years * 3600 * 24 * 365) - (days * 3600 * 24)
        hours = remain_seconds / 3600
        return hours

    def minutes(self):
        seconds = self.total_seconds()
        seconds = self.total_seconds()
        years = self.years()
        days = self.days()
        hours = self.hours()
        remain_seconds = seconds - (years * 3600 * 24 * 365) - (days * 3600 * 24) - (hours * 3600)
        minutes = remain_seconds / 60
        return minutes