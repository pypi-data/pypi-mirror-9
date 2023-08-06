from __future__ import absolute_import, division, print_function, unicode_literals

from nose.tools import assert_equal

from gazette import utils
from gazette.content_types import SimpleTextBox


class TestContentDictSerializer(object):
    def test_dumps_Content(self):
        ci = SimpleTextBox('hi', data=dict(message='Hello'))
        assert_equal(utils.ContentDictSerializer.dumps(ci),
                     {'name': 'hi',
                      'data': {'message': 'Hello'},
                      'version': None,
                      'content_type': 'simple-text-box',
                     })

    def test_dumps_other(self):
        other = {'foo': 'bar'}
        assert_equal(utils.ContentDictSerializer.dumps(other), other)

    def test_loads_Content(self):
        loaded = utils.ContentDictSerializer.loads(
            {'key': '/simple-text-box/hi',
             'name': 'hi',
             'data': {'message': 'Hello'},
             'version': None,
             'content_type': 'simple-text-box',
            })
        assert_equal(type(loaded), SimpleTextBox)
        assert_equal(loaded.name, 'hi')
        assert_equal(loaded.data, {'message': 'Hello'})
        assert_equal(loaded.version, None)

    def test_loads_other(self):
        other = {'foo': 'bar'}
        assert_equal(utils.ContentDictSerializer.loads(other), other)

    def test_full_cycle(self):
        ci = SimpleTextBox('hi', data=dict(message='Hello'))
        dumped = utils.ContentDictSerializer.dumps(ci)
        loaded = utils.ContentDictSerializer.loads(dumped)
        assert_equal(type(loaded), SimpleTextBox)
        assert_equal(loaded.name, 'hi')
        assert_equal(loaded.data, {'message': 'Hello'})
        assert_equal(loaded.version, None)


class TestMongoNonWrapDatastore(object):

    def test_put(self):
        import datastore.core
        base_ds = datastore.DictDatastore()
        mongo_wrap_ds = utils.MongoNonWrapDatastore(base_ds)

        mongo_wrap_ds.put(datastore.Key('/abc'),
                          {'foo': 'bar'})
        assert_equal(base_ds.get(datastore.Key('/abc')),
                     {'key': '/abc', 'foo':'bar'})