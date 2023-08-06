"""
Djinga backend for use in Django >= 1.8
"""

from inspect import getargspec
import jinja2

from django.template.backends.django import DjangoTemplates
from django.template.engine import _dirs_undefined
from django.utils.module_loading import import_string
from django.conf import settings

JJENV_OPTION_NAMES = getargspec(jinja2.environment.Environment.__init__)[0][1:]


class DjingaTemplates(DjangoTemplates):
    app_dirname = 'djinga'

    def __init__(self, params):

        options = params['OPTIONS']

        env = options.pop('environment', 'djinga.Environment')
        env_cls = import_string(env)

        jjenv_options_names = JJENV_OPTION_NAMES + \
                              getargspec(env_cls.__init__)[0][1:]

        jjenv_options = {}
        for k in list(options.keys()):
            if k in jjenv_options_names:
                jjenv_options[k] = options.pop(k)

        super(DjingaTemplates, self).__init__(params.copy())

        jjenv_options.setdefault('loader',
                           jinja2.FileSystemLoader(self.template_dirs))

        jjenv_options.setdefault('auto_reload', settings.DEBUG)
        jjenv_options.setdefault('undefined',
                                  jinja2.DebugUndefined
                                  if settings.DEBUG else jinja2.Undefined)

        self.env = env_cls(**jjenv_options)

    def from_string(self, template_code):
        return self.env.from_string(template_code)

    def get_template(self, template_name, dirs=_dirs_undefined):
        if self.env.use_jinja(template_name):
            return self.env.get_template(template_name)
        return super(DjingaTemplates, self).get_template(template_name, dirs)
