from __future__ import absolute_import, division, print_function, unicode_literals

import os.path
import shutil
from datetime import datetime
from time import sleep

from nose.tools import assert_equal, assert_raises, assert_not_equal

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


class TestWithStorage(object):
    this_dir = os.path.dirname(os.path.realpath(__file__))
    data_dir = os.path.join(this_dir, 'data')

    def setUp(self):
        sup = super(TestWithStorage, self)
        if hasattr(sup, 'setUp'):
            sup.setUp()

        # in-memory (isn't very realistic, no serialization/deserialization)
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
        sup = super(TestWithStorage, self)
        if hasattr(sup, 'tearDown'):
            sup.tearDown()
        shutil.rmtree(self.data_dir)
        Content.ds = None


class TestModelStorage(TestWithStorage):

    def test_get_item_missing(self):
        assert_equal(Content.get_by_fullname('/simple-text-box/foobar'),
                     None)

    def test_get_item_missing__show_empty(self):
        assert_equal(Content.get_by_fullname('/simple-text-box/foobar', show_empty=True).presentation_html(),
            '<div class="gazette" data-path="/simple-text-box/foobar">\nThere is no content created here yet.\n</div>')

    def test_get_item_missing__show_empty_str(self):
        assert_equal(
            Content.get_by_fullname('/simple-text-box/foobar', show_empty='No content yet').presentation_html(),
            '<div class="gazette" data-path="/simple-text-box/foobar">\nNo content yet\n</div>')

    def test_set_item_get_item(self):
        ci = SimpleTextBox('foo', data={'bar': 'baz'})
        ci.save()
        assert_equal(SimpleTextBox.get('foo').name,
                     ci.name)
        assert_equal(SimpleTextBox.get('foo').data,
                     ci.data)
        assert_equal(SimpleTextBox.get('foo').version,
                     1)
        assert_equal(type(SimpleTextBox.get('foo').timestamp),
                     datetime)
        assert_equal(Content.get_by_fullname('/simple-text-box/foo').name,
                     ci.name)
        assert_equal(Content.get_by_fullname('/simple-text-box/foo').data,
                     ci.data)
        assert_equal(Content.get_by_fullname('/simple-text-box/foo').version,
                     1)

        assert_equal(Content.get_by_fullname('simple-text-box/foo').name,
                     ci.name)

    def test_get_version(self):
        ci = SimpleTextBox('foo', data={'bar': 'baz'})
        ci.save()
        assert_equal(ci.version, 1)
        ci.data['bar'] = 'balloon'
        ci.save()
        assert_equal(ci.version, 2)
        assert_equal(SimpleTextBox.get('foo', version=1).data['bar'], 'baz')
        assert_equal(SimpleTextBox.get('foo', version=2).data['bar'], 'balloon')
        assert_equal(SimpleTextBox.get('foo').data['bar'], 'balloon')
        assert_equal(SimpleTextBox.get('foo', version=3), None)


    def test_list_versions(self):
        ci = SimpleTextBox('foo', data={'bar': 'baz'})
        ci.save()
        sleep(0.01)
        ci.data['bar'] = 'yadda yadda'
        ci.save()
        sleep(0.01)
        ci.data['bar'] = 'asdfasdf'
        ci.save()

        versions = ci.versions()
        assert_equal(len(versions), 3)
        assert_not_equal(versions[0].timestamp, versions[1].timestamp)
        assert_not_equal(versions[1].timestamp, versions[2].timestamp)


        """
        Query examples

        def json_getattr(obj, field):
            return Query.object_getattr(jsonpickle.loads(obj), field)

        q = Query(Key('/simple-text-box/'), limit=10, object_getattr=json_getattr)
        q.filter('name', '=', 'foo2')
        q.order('-name')
        assert_equal([ci.name for ci in Content.ds.query(q)],
                     ['foo3', 'foo2', 'foo'])


        # TODO: need custom object_getattr for nested access, e.g. into data fields
        q = Query(Key('/simple-text-box/'), limit=10,
                  object_getattr=lambda obj, field: Query.object_getattr(jsonpickle.loads(obj), field))
        q.filter('data.bar', '=', 'baz')
        assert_equal(len(list(Content.ds.query(q))), 2)
        """


class TestContentFullName(object):
    def test_cls_str(self):
        assert_equal(content_full_name(SimpleTextBox, 'abc'),
                     '/simple-text-box/abc')

    def test_item(self):
        assert_equal(content_full_name(SimpleTextBox('abc')),
                     '/simple-text-box/abc')

    def test_invalid(self):
        with assert_raises(TypeError):
            content_full_name(Content, 'foo')

    def test_version(self):
        assert_equal(content_full_name(SimpleTextBox, 'abc', version=17),
                     '/simple-text-box/abc/17')
