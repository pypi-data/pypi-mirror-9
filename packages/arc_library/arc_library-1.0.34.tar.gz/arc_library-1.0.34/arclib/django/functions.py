# -*- coding: utf-8 -*-
import json

from datetime import datetime, time, date

from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect, Http404

# datetime -> String 변환 함수 ###
def day_to_string(value):
    if isinstance(value, datetime) or isinstance(value, date):
        return value.strftime('%Y.%m.%d')
    else:
        return u'None'

def minute_to_string(value):
    if isinstance(value, datetime):
        return value.strftime('%Y.%m.%d %H:%M')
    else:
        return u'None'

def time_to_string(value):
    if isinstance(value, datetime):
        return value.strftime('%H:%M')
    else:
        return u'None'

def datetime_to_string(instance, string_format='%Y.%m.%d %H:%M:%S'):
    if isinstance(instance, datetime):
        return instance.strftime(string_format)
    elif isinstance(instance, date):
        if string_format == '%Y.%m.%d %H:%M:%S':
            string_format = '%Y.%m.%d'
        return instance.strftime(string_format)
    else:
        return '0000.00.00 00:00:00'


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


'''
    두 점 사이의 거리 계산 공식
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
'''
from math import radians, cos, sin, asin, sqrt
def distance(lat1, lon1, lat2, lon2):
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 

    # 6367 km is the radius of the Earth
    km = 6367 * c
    return km 

'''
페이스북 사진 가져오는 함수
'''
def get_facebook_profile_url(facebook_id):
    url = 'https://graph.facebook.com/%s/picture?type=large' % (facebook_id)
    return url
    
def get_facebook_profile_image(facebook_id):
    url = 'https://graph.facebook.com/%s/picture?type=large' % (facebook_id)

