# -*- coding: utf-8 -*-
import json
from django.http import HttpResponse, HttpResponseRedirect, Http404

import logging
import sys
log = logging.getLogger(__name__)

handler = logging.StreamHandler(stream=sys.stdout)
handler.setLevel(logging.DEBUG)

log.addHandler(handler)
log.setLevel(logging.DEBUG)

'''
Django에서 Response에 넣을 JSONObject 클래스
'''
class ArcReturnJSONObject:
    RESULT_STATE_SUCCESS = 'success';
    RESULT_STATE_FAILURE = 'failure';

    dict = {
        'result': RESULT_STATE_SUCCESS,
        'message': '',
        'data': {},
    }

    '''
    생성자
        인자가 없을 경우 : 성공여부 success로 시작
        인자가 1개 : 성공여부 추가
        인자가 2개 : 성공여부, 메시지 추가
    '''
    def __init__(self, *args):
        self.dict.clear()
        self.dict['result'] = self.RESULT_STATE_FAILURE
        self.dict['message'] = ''
        self.dict['data'] = {}

        len_args = len(args)
        if len_args == 0:
            pass
        if len_args >= 1:
            if isinstance(args[0], bool):
                if args[0]:
                    self.dict['result'] = self.RESULT_STATE_SUCCESS
                elif not args[0]:
                    self.dict['result'] = self.RESULT_STATE_FAILURE
        if len_args == 2:
            if isinstance(args[1], str) or isinstance(args[1], unicode):
                self.dict['message'] = args[1]
        

    # 결과가 성공인지, 실패인지
    def set_state(self, value):
        if value:
            self.dict['result'] = self.RESULT_STATE_SUCCESS
        else:
            self.dict['result'] = self.RESULT_STATE_FAILURE

    def set_message(self, value):
        self.dict['message'] = value

    # Object 삽입
    def add_object(self, key, value):
        self.dict['data'][key] = value

    # .json()함수가 있는 경우, 해당 value를 .json()후 넣어줌
    def add_object_to_json(self, key, value):
        self.dict['data'][key] = value.json()

    def add_array_to_json(self, key, array):
        data_array = []
        for item in array:
            data_array.append(item.json())
        self.dict['data'][key] = data_array

    def json_response(self):
        return HttpResponse(json.dumps(self.dict), content_type='application/json')

    def json_dumps(self):
        return json.dumps(self.dict)

    def json_loads(self, string):
        dict = json.loads(string)
        try:
            result = dict['result']
            message = dict['message']
            data = dict['data']

            self.dict['result'] = result
            self.dict['message'] = message
            self.dict['data'] = data
        except Exception as e:
            log.debug(e.args)

    def get_result(self):
        return self.dict['result']

    def get_message(self):
        return self.dict['message']

    def get_data(self):
        return self.dict['data']

    def get_result_bool(self):
        if self.get_result() == self.RESULT_STATE_SUCCESS:
            return True
        else:
            return False

    def log_dict(self, d, indent=0, log_print=True):
        if not log_print:
            return
        if isinstance(d, dict):
            for key, value in d.iteritems():
                if isinstance(value, dict):
                    log.debug(u'    %s%s' % (indent * ' ', key))
                    self.log_dict(value, indent + 1)
                elif isinstance(value, list):
                    log.debug(u'    %s%s' % (indent * ' ', key))
                    self.log_dict(value, indent + 1)
                else:
                    log.debug(u'    %s%s : %s' % (indent * ' ', key, value))
        elif isinstance(d, list):
            for index, item in enumerate(d):
                if isinstance(item, dict):
                    self.log_dict(item, indent + 1)
                    log.debug(u'\n')
                else:
                    log.debug(u'    %s%s' % (indent * ' ', item))
                    if index == len(d) - 1:
                        log.debug(u'\n')
        else:
            log.debug(u'  %s is not dict')

    def log(self, title=None, count=None, log_data=True):
        if count is not None and title is not None:
            log.debug(u'  [%s] %s info' % (count, title))
        elif title is not None:
            log.debug(u'  %s info' % (title))
        else:
            log.debug(u'  ArcReturnJSONObject info')

        log.debug(u'   Result : %s' % (self.get_result()))
        log.debug(u'   Message : %s' % (self.get_message()))
        log.debug(u'   Data\n')
        if log_data:
            self.log_dict(self.get_data())



# class ArcImage:
    