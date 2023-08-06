"""
Jinja2 template loaders for use in Django < 1.8
"""

from django.template.loaders import app_directories, filesystem

from . import engines


class DjingaLoaderBase(object):
    """
    Overrides django default template loader with Jinja2 depending on a
    user-defined condition (function returning a boolean)

    Also creates a jinja2 environment linked to this loader
    """

    def load_template(self, template_name, template_dirs=None):
        engines._init_env()

        if engines._env.use_jinja(template_name):
            template = engines._env.get_template(template_name)
            return template, template.filename

        return super(DjingaLoaderBase, self). \
            load_template(template_name, template_dirs)


class FileSystemLoader(DjingaLoaderBase, filesystem.Loader):
    pass


class AppLoader(DjingaLoaderBase, app_directories.Loader):
    pass
