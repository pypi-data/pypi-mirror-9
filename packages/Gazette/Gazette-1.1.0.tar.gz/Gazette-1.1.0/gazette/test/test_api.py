from __future__ import absolute_import, division, print_function, unicode_literals

import json

from nose.tools import assert_equal
from webtest import TestApp

from gazette.models import Content
from gazette.content_types import SimpleTextBox
from gazette.api import app as api_app
from gazette.test.test_models import TestWithStorage


class TestAPIBase(object):
    def setUp(self):
        sup = super(TestAPIBase, self)
        if hasattr(sup, 'setUp'):
            sup.setUp()

        api_app.catchall = False  # let errors bubble up, instead of a generic 500 page
        self.app = TestApp(api_app)


class TestAPI(TestAPIBase):
    def test_index(self):
        r = self.app.get('/')
        assert_equal(r.content_type, 'application/json')
        assert_equal(r.json['welcome'], 'This is the Gazette API')

    def test_404(self):
        r = self.app.get('/wrong', status=404)
        assert_equal(r.content_type, 'application/json')
        assert_equal(r.json['error'], 404)

    def test_types(self):
        r = self.app.get('/types')
        assert_equal(r.json, {'types': ['simple-text-box']})

    def test_preview(self):
        r = self.app.put_json('/preview/simple-text-box',
                              params={'message': 'just testing here <>'},
                              )
        assert_equal(r.content_type, 'text/html')
        assert_equal(r.body, 'just testing here &lt;&gt;')

    def test_preview_wrong_type(self):
        r = self.app.put_json('/preview/asdf3tqfes',
                              params={'message': 'just testing here'},
                              status=404)


class TestAPIWithDatastore(TestAPIBase, TestWithStorage):
    def test_get_content_404(self):
        r = self.app.get('/content/article/foo', status=404)

    def test_get_versions_404(self):
        r = self.app.get('/content/article/foo/all', status=404)

    def test_get_content_and_versions(self):
        content = SimpleTextBox('foo', data={'message': 'abcdef'})
        content.author = 'Bill'
        content.save()
        first_timestamp = content.timestamp
        content.data['message'] = 'new message'
        content.save()

        expected_current = {'name': 'foo',
                            'data': {'message': 'new message'},
                            'version': 2,
                            'content_type': 'simple-text-box',
                            'timestamp': content.timestamp.isoformat() + 'Z',
                            'author': 'Bill',
                            }
        r = self.app.get('/content/simple-text-box/foo')
        assert_equal(r.json, expected_current)

        r = self.app.get('/content/simple-text-box/foo/current')
        assert_equal(r.json, expected_current)

        r = self.app.get('/content/simple-text-box/foo/2')
        assert_equal(r.json, expected_current)

        r = self.app.get('/content/simple-text-box/foo/1')
        expected_v1 = expected_current.copy()
        expected_v1['version'] = 1
        expected_v1['data']['message'] = 'abcdef'
        expected_v1['timestamp'] = first_timestamp.isoformat() + 'Z'
        assert_equal(r.json, expected_v1)

        r = self.app.get('/content/simple-text-box/foo/3', status=404)

        r = self.app.get('/content/simple-text-box/foo/all')
        result_no_ts = r.json
        del result_no_ts['versions'][0]['timestamp']  # these change all the time :)
        del result_no_ts['versions'][1]['timestamp']
        assert_equal(result_no_ts, {'versions': [
            {'url': '/simple-text-box/foo/1',
             'version': 1,
             'author': 'Bill',
             },
            {'url': '/simple-text-box/foo/2',
             'version': 2,
             'author': 'Bill',
             },
        ]})

    def test_create_content(self):
        self.app.put_json('/content/simple-text-box/new',
                          params={'message': 'A new content has been born!'},
                          status=201,
                          )
        item = SimpleTextBox.get('new')
        assert_equal(item.name, 'new')
        assert_equal(item.data['message'], 'A new content has been born!')
        assert_equal(item.version, 1)

    def test_update_content(self):
        content = SimpleTextBox('existing', data={'message': 'xyz'})
        content.save()
        self.app.put_json('/content/simple-text-box/existing',
                          params={'message': 'xyz xyz xyz'},
                          status=200,
                          )
        item = SimpleTextBox.get('existing')
        assert_equal(item.name, 'existing')
        assert_equal(item.data['message'], 'xyz xyz xyz')
        assert_equal(item.version, 2)

    def test_create_with_author(self):
        self.app.put_json('/content/simple-text-box/new',
                          params={'message': 'A new content has been born!',
                                  'gazette.author': 'johndoe'},
                          status=201,
                          )
        item = SimpleTextBox.get('new')
        assert_equal(item.author, 'johndoe')

    def test_update_with_author(self):
        content = SimpleTextBox('existing', data={'message': 'xyz'}, author='johndoe')
        content.save()
        assert_equal(content.author, 'johndoe')
        self.app.put_json('/content/simple-text-box/existing',
                          params={'message': 'xyz xyz xyz',
                                  'gazette.author': 'George Washington'},
                          status=200,
                          )
        item = SimpleTextBox.get('existing')
        assert_equal(item.author, 'George Washington')

    def test_put_incomplete_path(self):
        self.app.put_json('/content/simple-text-box', params={'x': 'y'}, status=404)
        self.app.put_json('/content/asdfasdf', params={'x': 'y'}, status=404)
        self.app.put_json('/content/asdfasdf/asdf', params={'x': 'y'}, status=404)

    def test_put_wrong_content_type(self):
        self.app.put('/content/simple-text-box/foo', params={'message': 'xyz'}, status=415)
        self.app.put('/content/simple-text-box/foo',
                     headers={'Content-Type': b'application/json; charset=utf-8'},
                     params='{"message": "xyz"}',
                     status=201)

    def test_put_no_contents(self):
        self.app.put_json('/content/simple-text-box/foo', params={}, status=400)