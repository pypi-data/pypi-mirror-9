#!/usr/bin/env python
'''Chorus Client Test Cases'''

import logging
from pylibchorus.chorus_api import _login_
from pylibchorus.chorus_api import _logout_
from pylibchorus.chorus_api import _check_login_
from pylibchorus.chorus_api import _create_workfile_
from pylibchorus.chorus_api import _update_workfile_version_
from pylibchorus.chorus_api import _delete_workfile_
import sys
if sys.version_info[0] == 2 and sys.version_info[1] == 6:
    import unittest2 as unittest
else:
    import unittest

LOG = logging.getLogger(__name__)

def check_request_structure(testcase, request_obj):
    '''Test the request structure is correct'''
    testcase.assertIsNotNone(request_obj)
    testcase.assertIn('data', request_obj)
    testcase.assertIn('headers', request_obj)
    testcase.assertIn('params', request_obj)
    testcase.assertIn('cookies', request_obj)
    testcase.assertIn('url', request_obj)
    testcase.assertIn('method', request_obj)
    check_header(testcase, request_obj['headers'])

def check_header(testcase, header):
    '''Test the header object conforms to the what the API requires'''
    testcase.assertIsNotNone(header)
    testcase.assertIn('content-type', header)
    testcase.assertEquals(header['content-type'],
                          'application/x-www-form-urlencoded')

def check_params(testcase, params, expected_sid):
    '''Check the params object contains the correct session_id'''
    testcase.assertIsNotNone(params)
    testcase.assertIn('session_id', params)
    testcase.assertEqual(params['session_id'], expected_sid)

class ChorusSessionTests(unittest.TestCase):
    '''ChorusSession Test Case'''

    def test_login_returns_request_data(self):
        '''Test _login_ returns request data'''
        actual = _login_('chorusadmin', 'secret')
        check_request_structure(self, actual)
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
        check_header(self, actual['headers'])
        params = actual['params']
        self.assertIn('session_id', params)
        self.assertEquals(params['session_id'], '')
        self.assertEquals('/sessions?session_id=', actual['url'])
        self.assertEquals('POST', actual['method'])


    #pylint: disable=C0103
    def test_logout_returns_request_data(self):
        '''Test _logout_ returns correct request data'''
        sid = 'foobar'
        cookies = {'session_id': sid}
        actual = _logout_(sid, cookies)
        check_request_structure(self, actual)
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

    #pylint: disable=C0103
    def test_check_login_returns_request_data(self):
        '''Test _check_login_ returns correct request data'''
        sid = 'foobar'
        cookies = {'session_id': sid}
        actual = _check_login_(sid, cookies)
        check_request_structure(self, actual)
        self.assertIsNone(actual['data'])
        self.assertIsNotNone(actual['headers'])
        self.assertIsNone(actual['params'])
        self.assertIsNotNone(actual['cookies'])
        self.assertIsNotNone(actual['url'])
        self.assertIsNotNone(actual['method'])
        check_header(self, actual['headers'])
        self.assertEquals(cookies, actual['cookies'])
        self.assertEquals('/sessions', actual['url'])
        self.assertEquals('GET', actual['method'])

    #pylint: disable=C0103
    def test_create_workfile_returns_request_data(self):
        '''Test _create_workfile_ returns correct request data'''
        workspace_id = 1
        workfile_name = 'foo'
        sid = 'foobar'
        cookies = {'session_id': sid}
        actual = _create_workfile_(workspace_id, workfile_name, sid, cookies)
        check_request_structure(self, actual)
        self.assertIsNotNone(actual['data'])
        self.assertIsNotNone(actual['headers'])
        self.assertIsNotNone(actual['params'])
        self.assertIsNotNone(actual['cookies'])
        self.assertIsNotNone(actual['url'])
        self.assertIsNotNone(actual['method'])
        data = actual['data']
        self.assertIn('workspace_id', data)
        self.assertIn('file_name', data)
        self.assertEquals(workspace_id, data['workspace_id'])
        self.assertEquals(workfile_name, data['file_name'])
        check_header(self, actual['headers'])
        check_params(self, actual['params'], sid)
        self.assertEquals(cookies, actual['cookies'])
        self.assertEquals('/workspaces/%d/workfiles' % workspace_id,
                          actual['url'])
        self.assertEquals('POST', actual['method'])

    #pylint: disable=C0103
    def test_update_workfile_returns_request_data(self):
        '''Test _update_workfile_version_ returns correct request data'''
        userid = 1
        workfile_id = 1
        workfile = 'some long string that looks like code, somewhere'
        sid = 'foobar'
        cookies = {'session_id': sid}
        actual = _update_workfile_version_(
            userid,
            workfile_id,
            workfile,
            sid,
            cookies)
        check_request_structure(self, actual)
        check_params(self, actual['params'], sid)
        data = actual['data']
        self.assertIn('owner_id', data)
        self.assertIn('modifier_id', data)
        self.assertIn('commit_message', data)
        self.assertIn('content', data)
        self.assertEquals(data['owner_id'], userid)
        self.assertEquals(data['modifier_id'], userid)
        self.assertEquals(data['commit_message'], 'git commit')
        self.assertEquals(data['content'], workfile)
        self.assertEquals('/workfiles/1/versions', actual['url'])
        self.assertEquals('POST', actual['method'])

    def test_delete_workfile_returs_rquest_data(self):
        '''Test _delete_workfile_ returns correct request data'''
        workfile_id = 1
        sid = 'foobar'
        cookies = {'session_id': sid}
        actual = _delete_workfile_(workfile_id, sid, cookies)
        check_request_structure(self, actual)
        check_params(self, actual['params'], sid)
        self.assertIsNone(actual['data'])
        self.assertEquals('/workfiles/1', actual['url'])
        self.assertEquals('DELETE', actual['method'])
