"""
Base classes for extensions
"""

from django.utils import six

from jinja2 import nodes
from jinja2.ext import Extension


class SimpleTag(Extension):
    """
    Base class for a simple tag returning a constant string
    """
    abstract = True

    def parse(self, parser):
        six.next(parser.stream)
        args = []
        while parser.stream.current.type != 'block_end':
            args.append(parser.parse_expression())
        return nodes.Output([self.call_method('tag_func', args)])
