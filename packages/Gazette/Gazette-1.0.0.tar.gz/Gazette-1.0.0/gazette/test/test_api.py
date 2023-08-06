from __future__ import absolute_import, division, print_function, unicode_literals

from nose.tools import assert_equal
from webtest import TestApp

from gazette.models import Content
from gazette.content_types import SimpleTextBox
from gazette.api import app as api_app


class TestAPIBase(object):
    def setUp(self):
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


class TestAPIWithDatastore(TestAPIBase):
    def setUp(self):
        super(TestAPIWithDatastore, self).setUp()

        import datastore.core
        from gazette.utils import AutoKeyClassDatastore

        Content.ds = AutoKeyClassDatastore(datastore.DictDatastore())

    def test_get_content_404(self):
        r = self.app.get('/content/article/foo', status=404)

    def test_get_content(self):
        content = SimpleTextBox('foo', data={'message': 'abcdef'})
        content.save()
        r = self.app.get('/content/simple-text-box/foo')
        assert_equal(r.json,
                     {'name': 'foo',
                      'data': {'message': 'abcdef'},
                      'version': None,
                      'content_type': 'simple-text-box',
                     })

    def test_create_content(self):
        self.app.put_json('/content/simple-text-box/new',
                          params={'message': 'A new content has been born!'},
                          status=201,
        )
        item = SimpleTextBox.get('new')
        assert_equal(item.name, 'new')
        assert_equal(item.data['message'], 'A new content has been born!')

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
        # TODO assert version

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