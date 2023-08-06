#!/usr/bin/env python
'''Chorus Client Test Cases'''

import logging
from pylibchorus.chorus_client import _login_
from pylibchorus.chorus_client import _logout_
import unittest

LOG = logging.getLogger(__name__)

class ChorusSessionTests(unittest.TestCase):
    '''ChorusSession Test Case'''

    def test_login_returns_request_data(self):
        '''Test _login_ returns request data'''
        actual = _login_('chorusadmin', 'secret')
        self.assertIsNotNone(actual)
        self.assertIn('data', actual)
        self.assertIn('headers', actual)
        self.assertIn('params', actual)
        self.assertIn('cookies', actual)
        self.assertIn('url', actual)
        self.assertIn('method', actual)
        self.assertIsNotNone(actual['data'])
        self.assertIsNotNone(actual['headers'])
        self.assertIsNotNone(actual['params'])
        self.assertIsNone(actual['cookies'])
        self.assertIsNotNone(actual['url'])
        self.assertIsNotNone(actual['method'])
        data = actual['data']
        self.assertIn('username', data)
        self.assertIn('password', data)
        self.assertEquals(data['username'], 'chorusadmin')
        self.assertEquals(data['password'], 'secret')
        headers = actual['headers']
        self.assertIn('content-type', headers)
        self.assertEquals('application/x-www-form-urlencoded',
                          headers['content-type'])
        params = actual['params']
        self.assertIn('session_id', params)
        self.assertEquals(params['session_id'], '')
        self.assertEquals('/sessions?session_id=', actual['url'])
        self.assertEquals('POST', actual['method'])


    #pylint: disable=C0103
    def test_logout_returns_request_data(self):
        '''Test _logout_ returns correct request data'''
        sid = 'foobar'
        cookies = {'session_id', sid}
        actual = _logout_(sid, cookies)
        self.assertIsNotNone(actual)
        self.assertIn('data', actual)
        self.assertIn('headers', actual)
        self.assertIn('params', actual)
        self.assertIn('cookies', actual)
        self.assertIn('url', actual)
        self.assertIn('method', actual)
        self.assertIsNone(actual['data'])
        self.assertIsNotNone(actual['headers'])
        self.assertIsNotNone(actual['params'])
        self.assertIsNotNone(actual['cookies'])
        self.assertIsNotNone(actual['url'])
        self.assertIsNotNone(actual['method'])
        headers = actual['headers']
        self.assertIn('content-type', headers)
        self.assertEquals('application/x-www-form-urlencoded',
                          headers['content-type'])
        params = actual['params']
        self.assertIn('session_id', params)
        self.assertEquals(sid, params['session_id'])
        self.assertEquals(cookies, actual['cookies'])
        self.assertEquals('/sessions', actual['url'])
        self.assertEquals('DELETE', actual['method'])
