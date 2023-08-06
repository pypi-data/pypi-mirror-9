"""
Extensions for URL reversing
"""

from ._base import SimpleTag

from django.core.urlresolvers import reverse


class URLExtension(SimpleTag):
    tags = set(['url'])

    def tag_func(self, name, *args, **kwargs):
        return reverse(name, args=args, kwargs=kwargs)
