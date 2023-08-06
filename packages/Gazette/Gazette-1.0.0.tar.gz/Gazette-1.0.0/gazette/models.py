from __future__ import absolute_import, division, print_function, unicode_literals


class NoDatastoreConfigured(object):
    pass


class NoContentTypeNameDefined(object):
    pass


def content_full_name(cls_or_obj, name_if_cls=None):
    """
    Get the full name of a content item.

    :param cls_or_obj: A ``Content`` subclass or instance.
    :param str item_name: The item's name.  Only required if first parameter was a class (not an object instance).
    :return:
    """
    # TODO: versioning
    if name_if_cls:
        name = name_if_cls
    else:
        name = cls_or_obj.name
    return '/'.join(['', cls_or_obj.type_name, name])


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

    def __init__(self, name, version=None, data=None):
        """
        :param str name:
        :param int version:
        :param dict data:
        :return:
        """
        super(Content, self).__init__()
        self.name = name
        self.version = version
        self.data = data
        assert self.type_name
        self.content_type = self.type_name  # store a copy so its explicit in the API, etc

    def save(self):
        self.ds.put(content_full_name(self, self.name), self)

    @classmethod
    def get(cls, name, show_empty=False):
        """
        Gets a content instance.

        :param str name: short name of the content
        :param str show_empty: content not found, returns a placeholder HTML for content instead of returning ``None``.
            ``show_empty may be ``True`` for default placeholder or a string to specify the placeholder text
        :return: a content instance or ``None``
        """
        return cls.get_by_fullname(content_full_name(cls, name), show_empty=show_empty)

    @classmethod
    def get_by_fullname(cls, full_name, show_empty=False):
        """
        Gets a content instance.

        :param str name: full name of the content e.g. ``/article/foo``
        :param str show_empty: content not found, returns a placeholder HTML for content instead of returning ``None``.
            ``show_empty may be ``True`` for default placeholder or a string to specify the placeholder text
        :return: a content instance or ``None``
        """
        if not full_name.startswith('/'):
            full_name = '/' + full_name
        content = cls.ds.get(full_name)

        if not content and show_empty not in (False, None):
            from .content_types import all_content_types
            _, type_name, name = full_name.split('/')
            content_type = all_content_types()[type_name]
            content = content_type(name)
            if show_empty is True:
                placeholder_text = 'There is no content created here yet.'
            else:
                placeholder_text = show_empty
            content._render_html = lambda: placeholder_text

        return content

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
