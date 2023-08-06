from __future__ import absolute_import, division, print_function, unicode_literals

import os.path
import shutil

from nose.tools import assert_equal, assert_raises

from gazette.content_types import SimpleTextBox
from gazette.models import Content, content_full_name


class TestModels(object):
    def test_abstract(self):
        with assert_raises(NotImplementedError):
            Content('foo').presentation_html()
        with assert_raises(NotImplementedError):
            Content('foo')._render_html()

    def test_item(self):
        ci = SimpleTextBox('foo')


class TestModelStorage(object):
    this_dir = os.path.dirname(os.path.realpath(__file__))
    data_dir = os.path.join(this_dir, 'data')

    def setUp(self):
        # in-memory (isn't very realistic)
        # import datastore.core
        # from .utils import AutoKeyClassDatastore
        # Content.ds = AutoKeyClassDatastore(datastore.DictDatastore())

        import datastore.filesystem
        import datastore.core.serialize
        import jsonpickle

        jsonpickle.set_encoder_options('json', sort_keys=True, indent=2)
        Content.ds = datastore.core.SerializerShimDatastore(
            datastore.filesystem.FileSystemDatastore(self.data_dir),
            serializer=jsonpickle,  # conforms to dumps/loads protocol
        )

    def tearDown(self):
        shutil.rmtree(self.data_dir)


    def test_get_item_missing(self):
        assert_equal(Content.get_by_fullname('/simple-text-box/foobar'),
                     None)

    def test_get_item_missing__show_empty(self):
        assert_equal(Content.get_by_fullname('/simple-text-box/foobar', show_empty=True).presentation_html(),
                     '<div class="gazette" data-path="/simple-text-box/foobar">\nThere is no content created here yet.\n</div>')

    def test_get_item_missing__show_empty_str(self):
        assert_equal(Content.get_by_fullname('/simple-text-box/foobar', show_empty='No content yet').presentation_html(),
                     '<div class="gazette" data-path="/simple-text-box/foobar">\nNo content yet\n</div>')

    def test_set_item_get_item(self):
        ci = SimpleTextBox('foo', data={'bar': 'baz'})
        ci.save()
        assert_equal(SimpleTextBox.get('foo').name,
                     ci.name)
        assert_equal(SimpleTextBox.get('foo').data,
                     ci.data)
        assert_equal(Content.get_by_fullname('/simple-text-box/foo').name,
                     ci.name)
        assert_equal(Content.get_by_fullname('/simple-text-box/foo').data,
                     ci.data)

        assert_equal(Content.get_by_fullname('simple-text-box/foo').name,
                     ci.name)


    def test_query(self):
        # this is just for illustration purposes to show how queries can be done

        SimpleTextBox('foo', data={'bar': 'baz'}).save()
        SimpleTextBox('foo2', data={'bar': 'hey hey hey'}).save()
        SimpleTextBox('foo3', data={'bar': 'baz'}).save()

        from datastore.core.query import Query
        from datastore.core import Key
        import jsonpickle

        def json_getattr(obj, field):
            return Query.object_getattr(jsonpickle.loads(obj), field)

        q = Query(Key('/simple-text-box/'), limit=10, object_getattr=json_getattr)
        q.filter('name', '=', 'foo2')
        result = list(Content.ds.query(q))
        assert_equal(len(result), 1)
        assert_equal(result[0].data['bar'], 'hey hey hey')

        q = Query(Key('/simple-text-box/'), limit=10, object_getattr=json_getattr)
        q.order('-name')
        assert_equal([ci.name for ci in Content.ds.query(q)],
                     ['foo3', 'foo2', 'foo'])

        """
        # TODO: need custom object_getattr for nested access, e.g. into data fields
        q = Query(Key('/simple-text-box/'), limit=10,
                  object_getattr=lambda obj, field: Query.object_getattr(jsonpickle.loads(obj), field))
        q.filter('data.bar', '=', 'baz')
        assert_equal(len(list(Content.ds.query(q))), 2)
        """


class TestContentFullName(object):
    def test_content_full_name__cls_str(self):
        assert_equal(content_full_name(SimpleTextBox, 'abc'),
                     '/simple-text-box/abc')

    def test_content_full_name__item(self):
        assert_equal(content_full_name(SimpleTextBox('abc')),
                     '/simple-text-box/abc')

    def test_content_full_name__invalid(self):
        with assert_raises(TypeError):
            content_full_name(Content, 'foo')