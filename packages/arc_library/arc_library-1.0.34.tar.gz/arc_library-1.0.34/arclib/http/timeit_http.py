# -*- coding: utf-8 -*-
import os
import sys

import logging
log = logging.getLogger(__name__)
handler = logging.StreamHandler(stream=sys.stdout)
handler.setLevel(logging.DEBUG)
log.addHandler(handler)
log.setLevel(logging.DEBUG)

import json
import timeit
import requests

from arclib.django.object import ArcReturnJSONObject

class TimeitHttpClient:
    def __init__(self, title, url, method='post', params=None, files=None, repeat_number=1, loop=False, loop_count=1, handler=None):
        self.title = title
        self.url = url
        self.method = method
        self.params = params
        self.files = files
        self.repeat_number = repeat_number
        self.loop = loop
        self.loop_count = loop_count
        self.result_handler = handler

    # result_handler는 String result값을 받아 처리하는 함수
    # result(String)과 count(Integer)를 인자로 가짐
    def set_result_handler(self, handler):
        self.result_handler = handler

    def process(self, count):
        def request_http():
            if self.method == 'post':
                r = requests.post(self.url, data=self.params, files=self.files)
            else:
                r = requests.get(self.url, data=self.params)

            result = r.text
            self.result_handler(result, self.title, count)
        try:
            t = timeit.Timer(lambda : request_http())
            total_time = t.timeit(number=self.repeat_number)
            log.debug(u'  %s execution average time : %.02f (%s repeat)\n' %
                      (self.title, (total_time / self.repeat_number), self.repeat_number))
        except Exception as e:
            log.debug('Exception args : %s' % (e.args))
            log.debug('Exception : %s' % (e))
            raise Exception

    def execute(self):
        count = 0
        try:
            log.debug(u'\n-- %s measure execution time Start --\n' % (self.title))
            while True:
                self.process(count)
                count += 1
                if self.loop is not True and count == self.loop_count:
                    break
        except KeyboardInterrupt as e:
            log.debug(u'   !! User keyboard interrupt !!')
        finally:
            log.debug(u'\n-- %s measure execution time End --\n' % (self.title))