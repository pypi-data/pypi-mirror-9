#-*- coding: utf-8 -*-
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from arclib.django.object import ArcReturnJSONObject

def api(func):
    @csrf_exempt
    # @require_http_methods(["POST"])
    def wrap(request, *args, **kwargs):
        return func(request, *args, **kwargs)

    wrap.__doc__ = func.__doc__
    wrap.__name__ = func.__name__
    return wrap

def exception_json(func):
    def wrap(request, *args, **kwargs):
        try:
            # print 'exception_json try : %s' % (func.__name__)
            return func(request, *args, **kwargs)
        except Exception as e:
            print 'exception_json except : %s, %s' % (func.__name__, str(e.__class__))
            try:    exception_class = str(e.__class__)
            except: exception_class = 'get class failure'

            try:    exception_type = str(type(e))
            except: exception_type = 'get type failure'

            try:    exception_args = str(e.args)
            except: exception_args = 'get args failure'

            try:    exception = str(e)
            except: exception = 'get error failure'

            try:    str_request = str(request)
            except: str_request = 'get request failure'

            try:    str_request_get = str(request.GET)
            except: str_request_get = 'get request.GET failure'

            try:    str_request_post = str(request.POST)
            except: str_request_post = 'get request.POST failure'

            try:    str_request_files = str(request.FILES)
            except: str_request_files = 'get request.FILES failure'

            try:    str_request_path = str(request.path)
            except: str_request_path = 'get request.path failure'

            dict = {
                'class': exception_class,
                'type': exception_type,
                'exception': exception,
                'args': exception_args,
                'request': str_request,
                'request_get': str_request_get,
                'request_post': str_request_post,
                'request_files': str_request_files,
                'request_path': str_request_path,
            }
            jsondata = ArcReturnJSONObject(False, 'exception_json')
            jsondata.add_object('exception', dict)
            return jsondata.json_response()
    return wrap