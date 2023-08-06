#!/usr/bin/env python
'''Alpine/Chorus Client API Module'''

import logging
import requests

LOG = logging.Logger(name=__name__)

CONTENT_TYPE = 'application/x-www-form-urlencoded'
JSON_CONTENT_TYPE = 'application/json'

class ChorusSession(object):
    '''Chorus User Session Object'''

    def __init__(self, config):
        self.config = config
        self.sid = None
        self.cookies = None

    def __enter__(self):
        '''create session and return sid and cookies'''

        request_data = _login_(self.config.get('alpine', 'username'),
                               self.config.get('alpine', 'password'))

        LOG.debug("Opening Chorus Session")
        post = requests.post(self.get_url(request_data['url']),
                             params=request_data['params'],
                             data=request_data['data'],
                             headers=request_data['headers'])
        LOG.info("Status code for session open: %d", post.status_code)
        json = post.json()

        self.sid = json['response']['session_id']
        self.cookies = post.cookies
        return self

    def __exit__(self, _type, _value, _traceback):
        '''Close chorus session'''
        request_data = _logout_(self.sid, self.cookies)
        LOG.debug("Closing Chorus Session")
        delete = requests.delete(self.get_url(request_data['url']),
                                 params=request_data['params'],
                                 headers=request_data['headers'],
                                 cookies=request_data['cookies'])

        LOG.info("Status code for close: %d", delete.status_code)

    def get_url(self, path=""):
        '''Return the host and path for the chorus instance'''

        return "http://%s/%s" % (self.config.get('alpine', 'host'), path)

def _login_(username, password):
    '''Create Request Data for ChorusSession'''
    return {
        'data': {
            'username': username,
            'password': password,
        },
        'headers': {
            'content-type': CONTENT_TYPE,
        },
        'params': {
            'session_id': '',
        },
        'cookies': None,
        'url': '/sessions?session_id=',
        'method': 'POST',
    }

def _logout_(sid, cookies):
    '''Create request data for ChorusSession'''
    return {
        'data': None,
        'headers': {
            'content-type': CONTENT_TYPE,
        },
        'params': {
            'session_id': sid,
        },
        'cookies': cookies,
        'url': '/sessions',
        'method': 'DELETE',
    }
