from __future__ import absolute_import, division, print_function, unicode_literals

from nose.tools import assert_equal, assert_raises, assert_in, assert_not_in
from nose import SkipTest

from gazette.models import Content, JinjaPresentationContent
from gazette.content_types import SimpleTextBox, all_content_types
from gazette import utils


class TestSimpleTextBox(object):
    def test_name(self):
        s = SimpleTextBox('foo')
        assert_equal(s.type_name, 'simple-text-box')

    def test_presentation(self):
        s = SimpleTextBox('foo',
                          data={'message': 'hello, world! <>"'})
        assert_equal(s.presentation_html(),
                     '<div class="gazette" data-path="/simple-text-box/foo">\n'
                     'hello, world! &lt;&gt;&quot;\n'
                     '</div>')

    def test_presentation_nowrap(self):
        s = SimpleTextBox('foo',
                          data={'message': 'hello, world! <>"'})
        assert_equal(s.presentation_html(decorate_html=False),
                     'hello, world! &lt;&gt;&quot;')


def test_all_content_types():
    assert_equal(all_content_types()['simple-text-box'], SimpleTextBox)


def test_all_content_types_only_concrete():
    class Foo(Content):
        pass

    class FooBar(Foo):
        type_name = 'foobar'

        def presentation_html(self):
            return 'baz'

    assert_not_in(Foo, all_content_types().values())
    assert_in(FooBar, all_content_types().values())


class TestJinjaTemplate(object):
    try:
        import jinja2
    except ImportError:
        raise SkipTest

    def test_render_inline_template(self):
        import jinja2

        class JinjaH1inline(JinjaPresentationContent, Content):
            type_name = 'h1-message'

            @property
            def presentation_template(self):
                return jinja2.Template('<h1>{{ message }}</h1>')

        jh1 = JinjaH1inline('abcd', data={'message': 'hello, world!'})
        assert_equal(jh1.presentation_html(decorate_html=False),
                     '<h1>hello, world!</h1>')
        assert_equal(jh1.presentation_html(),
                     '<div class="gazette" data-path="/h1-message/abcd">\n'
                     '<h1>hello, world!</h1>\n'
                     '</div>')


    def test_render_loaded_template(self):
        import jinja2

        class JinjaH1loaded(JinjaPresentationContent, Content):
            type_name = 'h1-message'

            @property
            def presentation_template(self):
                return 'foo/bar/jinja_h1.html'

        j2env = jinja2.Environment(
            loader=jinja2.DictLoader({
                'foo/bar/jinja_h1.html': '<h1>{{ message }}</h1>',
            })
        )

        jh1 = JinjaH1loaded('abcd', data={'message': 'hello, world!'})
        jh1.j2env = j2env
        assert_equal(jh1.presentation_html(decorate_html=False),
                     '<h1>hello, world!</h1>')
        assert_equal(jh1.presentation_html(),
                     '<div class="gazette" data-path="/h1-message/abcd">\n'
                     '<h1>hello, world!</h1>\n'
                     '</div>')


    def test_abstract(self):
        with assert_raises(NotImplementedError):
            JinjaPresentationContent().presentation_template

    def test_show_empty(self):
        import jinja2
        import datastore.core

        class JinjaH1inline(JinjaPresentationContent, Content):
            type_name = 'h1-message'

            @property
            def presentation_template(self):
                return jinja2.Template('<h1>{{ message }}</h1>')

        with utils.push_config(Content, ds=utils.AutoKeyClassDatastore(datastore.DictDatastore())):
            html = JinjaH1inline.get('foobar', show_empty=True).presentation_html()
        assert_equal(html,
                     '<div class="gazette" data-path="/h1-message/foobar">\nThere is no content created here yet.\n</div>')