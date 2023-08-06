"""
Jinja2 environment container and functions, settings defaults and loader

(c) Thomas Khyn 2014
"""

import os
import sys
from importlib import import_module

import jinja2

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.template.base import TemplateDoesNotExist, TemplateSyntaxError
from django.utils import six

from .template import DjingaTemplate


class Environment(jinja2.Environment):
    """
    Jinja2 environment singleton subclass
    """

    template_class = DjingaTemplate

    def __init__(self,
                 filters=None,
                 globals=None,
                 load_from=(),
                 dj_exts=('html', 'htm', 'djhtml', 'djhtm'),  # django
                 jj_exts=('jjhtml', 'jjhtm'),  # jinja2
                 condition=None,
                 i18n_new_style=False,
                 **options):

        # fetch template extensions
        self.template_exts = []
        for s, exts in zip(('d', 'j'), [dj_exts, jj_exts]):
            if isinstance(exts, tuple):
                exts = list(exts)
            elif not isinstance(exts, list):
                raise ImproperlyConfigured(
                    '"%sj_exts" should be a tuple or list' % s)
            for i, ext in enumerate(exts):
                exts[i] = ext.lstrip('.')
            self.template_exts.extend(exts)

        self.use_jinja = condition or \
            (lambda path: os.path.splitext(path)[-1].lstrip('.') in jj_exts)

        super(Environment, self).__init__(**options)

        # automatically install i18n extension if USE_I18N is true
        if settings.USE_I18N:
            self.add_extension('jinja2.ext.i18n')
            from django.utils import translation
            self.install_gettext_translations(translation,
                                              newstyle=i18n_new_style)

        # add globally defined filters and globals from the settings
        self.filters.update(filters or {})
        self.globals.update(globals or {})

        # add filters and globals from custom modules
        for module_path in load_from:
            mod = import_module(module_path)
            for x in dir(mod):
                o = getattr(mod, x)
                if hasattr(o, '_jj_filter'):
                    self.filters[o._jj_name] = o
                elif hasattr(o, '_jj_global'):
                    self.globals[o._jj_name] = o

    @jinja2.utils.internalcode
    def get_template(self, *args, **kwargs):
        try:
            return super(Environment, self).get_template(*args, **kwargs)
        except jinja2.TemplateNotFound as exc:
            six.reraise(TemplateDoesNotExist,
                        TemplateDoesNotExist(exc.args), sys.exc_info()[2])
        except jinja2.TemplateSyntaxError as exc:
            six.reraise(TemplateSyntaxError,
                        TemplateSyntaxError(exc.args), sys.exc_info()[2])
