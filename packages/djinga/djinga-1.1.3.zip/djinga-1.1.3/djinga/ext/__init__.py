from .files import (
    StaticExtension as static,
    StaticCSSExtension as css,
    StaticJSExtension as js,
    MediaExtension as media
)

from .djangotags import (
    DjangoTag as django,
    CsrfToken as csrf_token
)
from .urls import URLExtension as url

from . import htmlcompress
