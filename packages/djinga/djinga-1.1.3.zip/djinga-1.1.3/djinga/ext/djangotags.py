"""
Extensions to use Django template language within Jinja2 templates
"""

from django import template as dj_template
from django.core.exceptions import ImproperlyConfigured
from django.utils import six

from jinja2 import nodes, contextfunction
from jinja2.ext import Extension
from jinja2 import Markup


class DjangoTag(Extension):
    # from https://github.com/coffin/coffin/pull/12/files?short_path=88b99bb#diff-e511b022f54e135b99f896c8fb355067R131

    tags = set(['django'])

    def preprocess(self, source, name, filename=None):
        source = source.replace('{% django %}', '{% django %}{% raw %}')
        source = source.replace('{% enddjango %}',
                                '{% endraw %}{% enddjango %}')
        return source

    def parse(self, parser):
        lineno = six.next(parser.stream).lineno
        while not six.next(parser.stream).test('block_end'):
            pass
        body = nodes.Const(six.next(parser.stream).value)
        while not parser.stream.current.test('block_end'):
            six.next(parser.stream)
        return nodes.Output([
            self.call_method('_django', args=[body], kwargs=[]),
        ]).set_lineno(lineno=lineno)

    @contextfunction
    def _django(self, context, html):
        request = context.get('request', None)
        if not request:
            raise ImproperlyConfigured(
                'You need to enable the django.core.context_processors.request '
                'context processor to use the {% django %} tag in Jinja2 '
                'templates.')
        context = dj_template.RequestContext(request, context)
        return dj_template.Template(html).render(context)


class CsrfToken(Extension):
    """
    Jinja2-version of the ``csrf_token`` tag.

    Adapted from a snippet by Jason Green:
    http://www.djangosnippets.org/snippets/1847/

    This tag is a bit stricter than the Django tag in that it doesn't
    simply ignore any invalid arguments passed in.

    Copied from Coffin, https://github.com/coffin/coffin
    (c) Coffin contributors
    3-clause BSD License
    """

    tags = set(['csrf_token'])

    def parse(self, parser):
        lineno = six.next(parser.stream).lineno
        return nodes.Output([
            self.call_method('_render', [nodes.Name('csrf_token', 'load')]),
        ]).set_lineno(lineno)

    def _render(self, csrf_token):
        from django.template.defaulttags import CsrfTokenNode
        return Markup(CsrfTokenNode().render({'csrf_token': csrf_token}))
