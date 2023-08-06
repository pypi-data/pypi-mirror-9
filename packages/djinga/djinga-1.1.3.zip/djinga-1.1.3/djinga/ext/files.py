"""
Extensions to serve static and media files
"""

from ._base import SimpleTag

from django.contrib.staticfiles.storage import staticfiles_storage
from django.conf import settings as dj_settings


class StaticExtension(SimpleTag):
    """Django-like static tag"""
    tags = set(['static'])

    def get_url(self, path, prefix=None):
        is_absolute = path.startswith('/') or ':' in path.split('/')[0]
        if not is_absolute:
            if prefix:
                path = '%s/%s' % (prefix, path)
            return staticfiles_storage.url(path)
        else:
            return path

    def tag_func(self, path):
        return self.get_url(path)


class StaticCSSExtension(StaticExtension):
    tags = set(['css'])

    def __init__(self, environment):
        super(StaticCSSExtension, self).__init__(environment)
        self.environment.css_dir = \
            getattr(dj_settings, 'JINJA2_STATIC_CSS', 'css')

    def tag_func(self, path):

        return '<link rel="stylesheet" type="text/css" href="%s">' % \
            self.get_url(path, self.environment.css_dir)


class StaticJSExtension(StaticExtension):
    tags = set(['js'])

    def __init__(self, environment):
        super(StaticJSExtension, self).__init__(environment)
        self.environment.js_dir = \
            getattr(dj_settings, 'JINJA2_STATIC_JS', 'js')

    def tag_func(self, path):
        return '<script type="text/javascript" src="%s"></script>' % \
            self.get_url(path, self.environment.js_dir)


class MediaExtension(SimpleTag):
    tags = set(['media'])

    def tag_func(self, path):
        is_absolute = path.startswith('/') or ':' in path.split('/')[0]
        if not is_absolute:
            return dj_settings.MEDIA_URL + path
        else:
            return path
