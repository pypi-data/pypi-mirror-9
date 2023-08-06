"""
Stack-In-A-Box: Basic Test
"""
import json
import logging
import unittest

import httpretty
import requests
import responses
import six

import stackinabox.util_httpretty
import stackinabox.util_responses
import stackinabox.util_requests_mock
from stackinabox.stack import StackInABox
from stackinabox.services.service import StackInABoxService


logger = logging.getLogger(__name__)


class AdvancedService(StackInABoxService):

    def __init__(self):
        super(AdvancedService, self).__init__('advanced')
        self.register(StackInABoxService.GET, '/',
                      AdvancedService.handler)
        self.register(StackInABoxService.GET, '/h',
                      AdvancedService.alternate_handler)
        self.register(StackInABoxService.GET, '/g',
                      AdvancedService.query_handler)

    def handler(self, request, uri, headers):
        return (200, headers, 'Hello')

    def alternate_handler(self, request, uri, headers):
        return (200, headers, 'Good-Bye')

    def query_handler(self, request, uri, headers):
        query = None
        if '?' in uri:
            path, querys = uri.split('?')
            querys = querys.replace(';', '&')
            query = {}
            for kv in querys.split('&'):
                k, v = kv.split('=')
                query[k] = v

            body = {}
            for k, v in query.items():
                body[k] = '{0}: Good-Bye {1}'.format(k, v)

            return (200, headers, json.dumps(body))
        else:
            logger.debug('No query string')
            return (200, headers, 'Where did you go?')


@httpretty.activate
class TestHttpretty(unittest.TestCase):

    def setUp(self):
        super(TestHttpretty, self).setUp()
        StackInABox.register_service(AdvancedService())

    def tearDown(self):
        super(TestHttpretty, self).tearDown()
        StackInABox.reset_services()

    def test_basic(self):
        stackinabox.util_httpretty.httpretty_registration('localhost')

        res = requests.get('http://localhost/advanced/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.text, 'Hello')

        res = requests.get('http://localhost/advanced/h')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.text, 'Good-Bye')

        expected_result = {
            'bob': 'bob: Good-Bye alice',
            'alice': 'alice: Good-Bye bob',
            'joe': 'joe: Good-Bye jane'
        }
        res = requests.get('http://localhost/advanced/g?bob=alice;'
                           'alice=bob&joe=jane')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json(), expected_result)


@unittest.skipIf(six.PY3, 'Responses fails on PY3')
def test_basic_responses():

    def run():
        responses.mock.start()
        StackInABox.register_service(AdvancedService())
        stackinabox.util_responses.responses_registration('localhost')

        res = requests.get('http://localhost/advanced/')
        assert res.status_code == 200
        assert res.text == 'Hello'

        res = requests.get('http://localhost/advanced/h')
        assert res.status_code == 200
        assert res.text == 'Good-Bye'

        expected_result = {
            'bob': 'bob: Good-Bye alice',
            'alice': 'alice: Good-Bye bob',
            'joe': 'joe: Good-Bye jane'
        }
        res = requests.get('http://localhost/advanced/g?bob=alice;'
                           'alice=bob&joe=jane')
        assert res.status_code == 200
        assert res.json() == expected_result

        StackInABox.reset_services()

        responses.mock.stop()
        responses.mock.reset()

    with responses.RequestsMock():
        run()


class TestRequestMock(unittest.TestCase):

    def setUp(self):
        super(TestRequestMock, self).setUp()
        StackInABox.register_service(AdvancedService())
        self.session = requests.Session()

    def tearDown(self):
        super(TestRequestMock, self).tearDown()
        StackInABox.reset_services()
        self.session.close()

    def test_basic(self):
        stackinabox.util_requests_mock.requests_mock_session_registration(
            'localhost', self.session)

        res = self.session.get('http://localhost/advanced/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.text, 'Hello')

        res = self.session.get('http://localhost/advanced/h')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.text, 'Good-Bye')

        expected_result = {
            'bob': 'bob: Good-Bye alice',
            'alice': 'alice: Good-Bye bob',
            'joe': 'joe: Good-Bye jane'
        }
        res = self.session.get('http://localhost/advanced/g?bob=alice;'
                               'alice=bob&joe=jane')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json(), expected_result)

    def test_context_requests_mock(self):
        with stackinabox.util_requests_mock.activate():
            stackinabox.util_requests_mock.requests_mock_registration(
                'localhost')

            res = requests.get('http://localhost/advanced/')
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res.text, 'Hello')

            res = requests.get('http://localhost/advanced/h')
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res.text, 'Good-Bye')

            expected_result = {
                'bob': 'bob: Good-Bye alice',
                'alice': 'alice: Good-Bye bob',
                'joe': 'joe: Good-Bye jane'
            }
            res = requests.get('http://localhost/advanced/g?bob=alice;'
                               'alice=bob&joe=jane')
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res.json(), expected_result)
