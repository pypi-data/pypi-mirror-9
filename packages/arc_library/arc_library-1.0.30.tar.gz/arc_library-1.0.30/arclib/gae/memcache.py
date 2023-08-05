# -*- coding: utf-8 -*-
import json
from google.appengine.api import memcache
CACHE_SIZE = 900000
FORMAT_KEY_NAME = '%s_split_%d'
FORMAT_KEY_COUNT = '%s_split_count'
FORMAT_KEY_TYPE = '%s_type'
TYPE_JSON = 'json'
TYPE_STRING = 'string'

'''
memcache 커스터마이징
자동으로 최대 캐시 크기만큼 split해서 저장/리턴 해준다
'''

def set_large(key, value, namespace=None):
    print '-- memcache.set start --'
    print '\tkey : %s' % (key)
    count = 0
    print '\tvalue : %s' % (value)
    print '\tdata length : %s' % (len(value))

    if isinstance(value, dict) or isinstance(value, list):
        data = json.dumps(value)
        memcache.set(namespace=namespace, key=FORMAT_KEY_TYPE % (key), value=TYPE_JSON)
    elif isinstance(value, str) or isinstance(value, unicode):
        data = value
        memcache.set(namespace=namespace, key=FORMAT_KEY_TYPE % (key), value=TYPE_JSON)
    else:
        return False

    while len(data) > 0:
        print '\t\twhile loop %s' % (count)
        cur_data = data[0:CACHE_SIZE]
        data = data[CACHE_SIZE:]
        cur_key_name = FORMAT_KEY_NAME % (key, count)
        memcache.set(namespace=namespace, key=cur_key_name, value=cur_data)
        count += 1
    cur_key_count = FORMAT_KEY_COUNT % (key)
    print '\tall count : %s' % (count)
    memcache.set(namespace=namespace, key=cur_key_count, value=count)
    return True
    # try:
    #     data = value
    #     count = 0
    #     while len(value) > 0:
    #         cur_data = data[0:CACHE_SIZE]
    #         data = data[CACHE_SIZE:]
    #         cur_key_name = FORMAT_KEY_NAME % (key, count)
    #         memcache.set(namespace=namespace, key=cur_key_name, value=cur_data)
    #         count += 1
    #     cur_key_count = FORMAT_KEY_COUNT % (key)
    #     memcache.set(namespace=namespace, key=cur_key_count, value=count)
    #     return True
    # except Exception as e:
    #     print type(e)
    #     print e.args
    #     print e
    #     return False

def get_large(key, namespace=None, convert_dict=None):
    print '-- memcache.get start --'
    cur_key_count = FORMAT_KEY_COUNT % (key)
    count = memcache.get(namespace=namespace, key=cur_key_count)
    type = memcache.get(namespace=namespace, key=FORMAT_KEY_TYPE % (key))
    print '\tkey : %s' % (key)

    if count is None:
        print '\tcount is None, return None'
        return None

    print '\tcount : %s' % (count)

    data_combine = ''
    for i in range(count):
        print '\t\tfor loop %s/%s' % (i + 1, count)
        cur_key_name = FORMAT_KEY_NAME % (key, i)
        cur_data = memcache.get(namespace=namespace, key=cur_key_name)

        if cur_data is None:
            print '\tfor loop except, cur_data is None. return None'
            return None
        data_combine += cur_data

    if type == TYPE_JSON and convert_dict == True:
        return json.loads(data_combine)
    else:
        return data_combine