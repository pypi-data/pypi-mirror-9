from __future__ import absolute_import, division, print_function, unicode_literals

from datetime import datetime
from operator import attrgetter

class NoDatastoreConfigured(object):
    pass


class NoContentTypeNameDefined(object):
    pass


def content_full_name(cls_or_obj, name_if_cls=None, version=None):
    """
    Get the full name of a content item.

    :param cls_or_obj: A ``Content`` subclass or instance.
    :param str item_name: The item's name.  Only required if first parameter was a class (not an object instance).
    :param version: int or 'current', or if a obj was passed in can be ``True`` to use obj's version
    :return:
    """
    if name_if_cls:
        name = name_if_cls
    else:
        name = cls_or_obj.name
    parts = ['', cls_or_obj.type_name, name]
    if version is True:
        version = getattr(cls_or_obj, 'version')
    if version:
        parts.append(str(version))
    return '/'.join(parts)


class Content(object):
    """
    A definition of content, particularly the templates to show & edit it.

    Subclasses should be used to define specific types (e.g. "blog post")

    Instances of one of a subclasses will hold actual content data (e.g. "Dec 3 blog entry")
    """

    ds = NoDatastoreConfigured

    type_name = NoContentTypeNameDefined()

    def _render_html(self):
        """
        Render the HTML.  Any decoration, extra handling, etc should be done in ``presentation_html()``
        """
        raise NotImplementedError

    def __init__(self, name, version=0, data=None, timestamp=None, author=None):
        """
        :param str name:
        :param dict data:
        :return:
        """
        super(Content, self).__init__()
        self.name = name
        self.version = version
        self.data = data
        self.timestamp = timestamp
        self.author = author
        assert self.type_name
        self.content_type = self.type_name  # store a copy so its explicit in the API, etc

    def save(self):
        self.version += 1
        self.timestamp = datetime.utcnow()
        self.ds.put(content_full_name(self, self.name, self.version), self)
        self.ds.put(content_full_name(self, self.name, 'current'), self)

    @classmethod
    def get(cls, name, show_empty=False, version='current'):
        """
        Gets a content instance.

        :param str name: short name of the content
        :param str show_empty: content not found, returns a placeholder HTML for content instead of returning ``None``.
            ``show_empty may be ``True`` for default placeholder or a string to specify the placeholder text
        :param int version: version number to fetch, or current
        :return: a content instance or ``None``
        """
        return cls.get_by_fullname(content_full_name(cls, name, version), show_empty=show_empty)

    @classmethod
    def get_by_fullname(cls, full_name, show_empty=False):
        """
        Gets a content instance.

        :param str full_name: full name of the content with or without version e.g. ``/article/foo`` or ``/article/foo/3``
        :param str show_empty: content not found, returns a placeholder HTML for content instead of returning ``None``.
            ``show_empty may be ``True`` for default placeholder or a string to specify the placeholder text
        :return: a content instance or ``None``
        """
        if not full_name.startswith('/'):
            full_name = '/' + full_name
        if full_name.count('/') == 2:
            full_name += '/current'
        content = cls.ds.get(full_name)

        if not content and show_empty not in (False, None):
            from .content_types import all_content_types

            _, type_name, name, version = full_name.split('/')
            content_type = all_content_types()[type_name]
            content = content_type(name)
            if show_empty is True:
                placeholder_text = 'There is no content created here yet.'
            else:
                placeholder_text = show_empty
            content._render_html = lambda: placeholder_text

        return content

    def versions(self):
        from datastore.core.query import Query
        from datastore.core import Key

        q = Query(Key(content_full_name(self)))
        versions = sorted(Content.ds.query(q), key=attrgetter('version'))
        # last two should be same, due to "current" doc being duplicated
        if versions[-1].version == versions[-2].version:
            versions.pop()
        return versions

    def presentation_html(self, decorate_html=True):
        # output the text, no other HTML here
        html = self._render_html()
        if decorate_html:
            html = self._wrap_html(html)
        return html

    def _wrap_html(self, html):
        return self._wrap_html_template(html, content_full_name(self))

    @staticmethod
    def _wrap_html_template(html, full_name):
        return '<div class="gazette" data-path="{}">\n{}\n</div>'.format(full_name, html)


try:
    import jinja2
except ImportError:
    pass
else:

    class JinjaPresentationContent(object):
        '''
        A mixin to implement presentation_html via a template.

        Set the ``j2env`` attribute at either the class or instance level to specify your jinja environment settings
        '''

        j2env = jinja2.Environment()

        def _render_html(self):
            return self.j2env.get_or_select_template(self.presentation_template).render(self.data)

        def presentation_html(self, *args, **kwargs):
            output = super(JinjaPresentationContent, self).presentation_html(*args, **kwargs)
            return jinja2.Markup(output)

        @property
        def presentation_template(self):
            '''
            :return: a template or list of template names to be loaded from the jinja Environment, or a jinja2.Template object
            '''
            raise NotImplementedError
