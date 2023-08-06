import json
import logging

import mock
import six

from cliquet import logger
from cliquet.logging import MozillaHekaRenderer, ClassicLogRenderer

from .support import BaseWebTest, unittest


def logger_context():
    return logger._context._dict


class ClassicLogRendererTest(unittest.TestCase):
    def setUp(self):
        self.renderer = ClassicLogRenderer({})

    def test_output_is_serialized_as_string(self):
        value = self.renderer(self.logger, 'debug', {})
        self.assertIsInstance(value, six.string_types)

    def test_values_are_defaulted_to_question_mark(self):
        value = self.renderer(self.logger, 'debug', {})
        self.assertIn('?', value)



class MozillaHekaRendererTest(unittest.TestCase):
    def setUp(self):
        self.renderer = MozillaHekaRenderer({})
        self.logger = logging.getLogger(__name__)

    def test_output_is_serialized_json(self):
        value = self.renderer(self.logger, 'debug', {})
        self.assertIsInstance(value, six.string_types)

    def test_standard_entries_are_filled(self):
        import os

        with mock.patch('cliquet.utils.msec_time', return_value=12):
            value = self.renderer(self.logger, 'debug', {})

        log = json.loads(value)
        self.assertDictEqual(log, {
            'EnvVersion': '2.0',
            'Hostname': os.uname()[1],
            'Logger': None,
            'Pid': os.getpid(),
            'Severity': 7,
            'Timestamp': 12000000,
            'Type': '',
            'Fields': {}
        })

    def test_standard_entries_are_not_overwritten(self):
        value = self.renderer(self.logger, 'debug', {'Hostname': 'her'})
        log = json.loads(value)
        self.assertEqual(log['Hostname'], 'her')

    def test_type_comes_from_structlog_event(self):
        value = self.renderer(self.logger, 'debug', {'event': 'booh'})
        log = json.loads(value)
        self.assertEqual(log['Type'], 'booh')

    def test_severity_comes_from_logger_name(self):
        value = self.renderer(self.logger, 'critical', {})
        log = json.loads(value)
        self.assertEqual(log['Severity'], 0)

    def test_unknown_fields_are_moved_to_fields_entry(self):
        value = self.renderer(self.logger, 'critical', {'win': 11})
        log = json.loads(value)
        self.assertEqual(log['Fields'], {'win': 11})

    def test_fields_can_be_provided_directly(self):
        value = self.renderer(self.logger, 'critical', {'Fields': {'win': 11}})
        log = json.loads(value)
        self.assertEqual(log['Fields'], {'win': 11})


class RequestSummaryTest(BaseWebTest, unittest.TestCase):
    def test_request_summary_is_sent_as_info(self):
        with mock.patch('cliquet.logger.info') as mocked:
            self.app.get('/')
            mocked.assert_called_with('request.summary')

    def test_standard_info_is_bound(self):
        self.app.get('/', headers=self.headers)
        event_dict = logger_context()
        self.assertEqual(event_dict['path'], '/v0/')
        self.assertEqual(event_dict['method'], 'GET')
        self.assertEqual(event_dict['code'], 200)
        self.assertIsNotNone(event_dict['uid'])
        self.assertIsNotNone(event_dict['time'])
        self.assertIsNotNone(event_dict['t'])
        self.assertIsNone(event_dict['agent'])
        self.assertIsNone(event_dict['lang'])
        self.assertIsNone(event_dict['errno'])

    def test_userid_is_none_when_anonymous(self):
        self.app.get('/')
        event_dict = logger_context()
        self.assertIsNone(event_dict['uid'])

    def test_lang_is_not_none_when_provided(self):
        self.app.get('/', headers={'Accept-Language': 'fr-FR'})
        event_dict = logger_context()
        self.assertEqual(event_dict['lang'], 'fr-FR')

    def test_agent_is_not_none_when_provided(self):
        self.app.get('/', headers={'User-Agent': 'webtest/x.y.z'})
        event_dict = logger_context()
        self.assertEqual(event_dict['agent'], 'webtest/x.y.z')

    def test_errno_is_specified_on_error(self):
        self.app.get('/unknown', status=404)
        event_dict = logger_context()
        self.assertEqual(event_dict['errno'], 111)

    def test_auth_type_is_bound(self):
        self.app.get('/mushrooms', headers=self.headers)
        event_dict = logger_context()
        self.assertEqual(event_dict['auth_type'], 'FxA')
        # XXX: 401 ?
        # self.app.get('/mushrooms',
        #              headers={'Authorization': 'Basic bmlrbzpuaWtv'})
        # event_dict = logger_context()
        # self.assertEqual(event_dict['auth_type'], 'Basic')


class BatchSubrequestTest(BaseWebTest, unittest.TestCase):
    def setUp(self):
        super(BatchSubrequestTest, self).setUp()
        headers = self.headers.copy()
        headers['User-Agent'] = 'readinglist'
        body = {
            'requests': [{
                'path': '/unknown',
                'headers': {'User-Agent': 'foo'}
            }]
        }
        self.app.post_json('/batch', body, headers=headers)

    def test_batch_global_request_is_preserved(self):
        event_dict = logger_context()
        self.assertEqual(event_dict['code'], 200)
        self.assertEqual(event_dict['path'], '/batch')
        self.assertEqual(event_dict['agent'], 'readinglist')

    def test_batch_size_is_bound(self):
        event_dict = logger_context()
        self.assertEqual(event_dict['batch_size'], 1)

    def test_subrequest_summaries_are_logged(self):
        # XXX: how ?
        pass


class ResourceInfoTest(BaseWebTest, unittest.TestCase):
    def test_resource_name_is_bound(self):
        self.app.get('/mushrooms', headers=self.headers)
        event_dict = logger_context()
        self.assertEqual(event_dict['resource_name'], 'mushroom')

    def test_resource_timestamp_is_bound(self):
        r = self.app.get('/mushrooms', headers=self.headers)
        event_dict = logger_context()
        self.assertEqual(event_dict['resource_timestamp'],
                         int(r.headers['Last-Modified']))

    def test_result_size_and_limit_are_bound(self):
        self.app.post_json('/mushrooms', {'name': 'a'}, headers=self.headers)
        self.app.post_json('/mushrooms', {'name': 'b'}, headers=self.headers)
        self.app.post_json('/mushrooms', {'name': 'c'}, headers=self.headers)

        self.app.get('/mushrooms?_limit=5', headers=self.headers)
        event_dict = logger_context()
        self.assertEqual(event_dict['limit'], 5)
        self.assertEqual(event_dict['nb_records'], 3)
