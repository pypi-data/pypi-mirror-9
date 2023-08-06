from __future__ import absolute_import, division, print_function, unicode_literals

from cgi import escape

from . import models


class SimpleTextBox(models.Content):
    type_name = 'simple-text-box'

    def _render_html(self):
        return escape(self.data['message'], quote=True)


def all_content_types(StartingClass=models.Content):
    """
    :param:
    :return: a dict of str type_name => Content subclass
    """
    class_map = dict()
    for cls in StartingClass.__subclasses__():
        if not isinstance(cls.type_name, models.NoContentTypeNameDefined):
            class_map[cls.type_name] = cls
        class_map.update(all_content_types(cls))
    return class_map


