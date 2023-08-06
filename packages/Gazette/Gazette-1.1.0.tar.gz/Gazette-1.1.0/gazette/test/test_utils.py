from __future__ import absolute_import, division, print_function, unicode_literals

from datetime import datetime

from nose.tools import assert_equal

from gazette import utils
from gazette.content_types import SimpleTextBox
from gazette.models import Content


class TestContentDictSerializer(object):
    def test_dumps_Content(self):
        ci = SimpleTextBox('hi', data=dict(message='Hello'))
        assert_equal(utils.ContentDictSerializer.dumps(ci),
                     {'name': 'hi',
                      'data': {'message': 'Hello'},
                      'version': 0,
                      'content_type': 'simple-text-box',
                      'timestamp': None,
                      'author': None,
                     })

    def test_dumps_other(self):
        other = {'foo': 'bar'}
        assert_equal(utils.ContentDictSerializer.dumps(other), other)

    def test_loads_Content(self):
        loaded = utils.ContentDictSerializer.loads(
            {'key': '/simple-text-box/hi',
             'name': 'hi',
             'data': {'message': 'Hello'},
             'version': 123,
             'content_type': 'simple-text-box',
             'timestamp': datetime(2000, 1, 1, 12, 30)
        })
        assert_equal(type(loaded), SimpleTextBox)
        assert_equal(loaded.name, 'hi')
        assert_equal(loaded.data, {'message': 'Hello'})
        assert_equal(loaded.version, 123)
        assert_equal(loaded.timestamp, datetime(2000, 1, 1, 12, 30))

    def test_loads_other(self):
        other = {'foo': 'bar'}
        assert_equal(utils.ContentDictSerializer.loads(other), other)

    def test_full_cycle(self):
        import datastore.core
        with utils.push_config(Content, ds=utils.AutoKeyClassDatastore(datastore.DictDatastore())):
            ci = SimpleTextBox('hi', data=dict(message='Hello'))
            ci.save()  # force timestamp to be set
        dumped = utils.ContentDictSerializer.dumps(ci)
        loaded = utils.ContentDictSerializer.loads(dumped)
        assert_equal(type(loaded), SimpleTextBox)
        # check that ALL attributes are the same
        for attr in dir(ci):
            if attr.startswith('__'):
                continue
            if callable(getattr(ci, attr)):
                continue
            assert_equal(getattr(ci, attr),
                         getattr(loaded, attr))


class TestMongoNonWrapDatastore(object):

    def test_put(self):
        import datastore.core
        base_ds = datastore.DictDatastore()
        mongo_wrap_ds = utils.MongoNonWrapDatastore(base_ds)

        mongo_wrap_ds.put(datastore.Key('/abc'),
                          {'foo': 'bar'})
        assert_equal(base_ds.get(datastore.Key('/abc')),
                     {'key': '/abc', 'foo':'bar'})


try:
    import datastore.mongo
except ImportError:
    pass
else:
    def test_GazetteMongoDatastore():
        from datastore.core import Key
        assert_equal(
            utils.GazetteMongoDatastore._collectionNameForKey(Key('/foo-bar/baz/7')),
            'foo_bar'
        )