import json

import mock

from .support import BaseWebTest, FakeAuthentMixin, unittest


MINIMALIST_RECORD = {'name': 'Champignon'}


class CORSOriginHeadersTest(FakeAuthentMixin, BaseWebTest, unittest.TestCase):
    def setUp(self):
        super(CORSOriginHeadersTest, self).setUp()
        self.headers['Origin'] = 'notmyidea.org'

        response = self.app.post_json(self.collection_url,
                                      MINIMALIST_RECORD,
                                      headers=self.headers,
                                      status=201)
        self.record = response.json

    def test_present_on_hello(self):
        response = self.app.get('/',
                                headers=self.headers,
                                status=200)
        self.assertIn('Access-Control-Allow-Origin', response.headers)

    def test_present_on_single_record(self):
        response = self.app.get(self.get_item_url(),
                                headers=self.headers)
        self.assertIn('Access-Control-Allow-Origin', response.headers)

    def test_present_on_deletion(self):
        response = self.app.delete(self.get_item_url(),
                                   headers=self.headers)
        self.assertIn('Access-Control-Allow-Origin', response.headers)

    def test_present_on_unknown_record(self):
        url = self.get_item_url('unknown')
        response = self.app.get(url,
                                headers=self.headers,
                                status=404)
        self.assertIn('Access-Control-Allow-Origin', response.headers)

    def test_present_on_invalid_record_update(self):
        body = {'name': 42}
        response = self.app.patch_json(self.get_item_url(),
                                       body,
                                       headers=self.headers,
                                       status=400)
        self.assertIn('Access-Control-Allow-Origin', response.headers)

    def test_present_on_successful_creation(self):
        response = self.app.post_json(self.collection_url,
                                      MINIMALIST_RECORD,
                                      headers=self.headers,
                                      status=201)
        self.assertIn('Access-Control-Allow-Origin', response.headers)

    def test_present_on_invalid_record_creation(self):
        body = {'name': 42}
        response = self.app.post_json(self.collection_url,
                                      body,
                                      headers=self.headers,
                                      status=400)
        self.assertIn('Access-Control-Allow-Origin', response.headers)

    def test_present_on_readonly_update(self):
        with mock.patch('cliquet.tests.testapp.views.'
                        'MushroomSchema.is_readonly',
                        return_value=True):
            body = {'name': 'Amanite'}
            response = self.app.patch_json(self.get_item_url(),
                                           body,
                                           headers=self.headers,
                                           status=400)
        self.assertEqual(response.json['message'], 'Cannot modify name')
        self.assertIn('Access-Control-Allow-Origin', response.headers)

    def test_present_on_unauthorized(self):
        self.headers.pop('Authorization', None)
        response = self.app.post_json(self.collection_url,
                                      MINIMALIST_RECORD,
                                      headers=self.headers,
                                      status=401)
        self.assertIn('Access-Control-Allow-Origin', response.headers)

    def test_present_on_internal_error(self):
        with mock.patch('cliquet.resource.BaseResource.get_records',
                        side_effect=ValueError):
            response = self.app.get('/mushrooms',
                                    headers=self.headers, status=500)
        self.assertIn('Access-Control-Allow-Origin', response.headers)


def get_exposed_headers(headers):
    access_control_headers = headers['Access-Control-Expose-Headers']
    return [x.strip() for x in access_control_headers.split(',')]


class CORSExposeHeadersTest(FakeAuthentMixin, BaseWebTest):
    def test_present_on_collection_get(self):
        response = self.app.get(self.collection_url,
                                headers=self.headers)
        expose_headers = response.headers['Access-Control-Expose-Headers']
        self.assertEqual('Backoff, Retry-After, Last-Modified, Total-Records, Alert, Next-Page', expose_headers)

class CORSExposeHeadersTest(BaseWebTest, unittest.TestCase):
    def assert_headers_present(self, method, path, allowed_headers):
        if allowed_headers is None:
            return
        self.headers.update({'Origin': 'lolnet.org'})
        http_method = getattr(self.app, method.lower())
        response = http_method(path, headers=self.headers)
        self.assertIn('Access-Control-Expose-Headers', response.headers)
        exposed_headers = get_exposed_headers(response.headers).sort()
        self.assertEqual(allowed_headers.sort(), exposed_headers)

    def test_preflight_headers_are_set_for_default_endpoints(self):
        self.assert_headers_present('GET', '/',
                                    ['Alert', 'Backoff', 'Retry-After'])

    def test_preflight_headers_are_set_for_collection_get(self):
        self.assert_headers_present('GET', '/mushrooms', [
            'Alert', 'Backoff', 'Retry-After', 'Last-Modified',
            'Total-Records', 'Next-Page'])

    def test_preflight_headers_are_set_for_record_get(self):
        resp = self.app.post('/mushrooms', json.dumps({'name': 'Bolet'}),
                             headers=self.headers, status=201)
        self.assert_headers_present('GET', '/mushrooms/%s' % resp.json['id'], [
            'Alert', 'Backoff', 'Retry-After', 'Last-Modified'])
