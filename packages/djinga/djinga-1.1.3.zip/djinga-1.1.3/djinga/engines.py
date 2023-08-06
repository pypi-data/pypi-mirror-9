try:
    from django.template import engines
except ImportError:
    # hack for django < 1.8

    import jinja2

    from django.template import loader
    from django.conf import settings

    _env = None

    def _init_env(**options):
        """
        Initialise the environment that is going to be used in the loaders
        """
        global _env

        if _env:
            return

        from .environment import Environment

        template_dirs = [x for ldr_str in settings.TEMPLATE_LOADERS \
            for x in loader.find_template_loader(ldr_str) \
                           .get_template_sources('')]

        settings_options = dict(
            loader=jinja2.FileSystemLoader(template_dirs),
            extensions=getattr(settings, 'JINJA2_EXTENSIONS', {})
        )
        settings_options.update(getattr(settings, 'JINJA2_ENV_ARGS', {}))

        options = dict(settings_options, **options)

        _env = Environment(**options)

        _env.filters.update(getattr(settings, 'JINJA2_FILTERS', {}))
        _env.globals.update(getattr(settings, 'JINJA2_GLOBALS', {}))

    class DummyEngine(object):
        def __init__(self):
            self.debug = settings.TEMPLATE_DEBUG

    class DummyBackend(object):

        def __init__(self):
            self.engine = DummyEngine()

        @property
        def env(self):
            _init_env()
            return _env

        def from_string(self, *args, **kwargs):
            return self.env.from_string(*args, **kwargs)

    engines = {
        'djinga': DummyBackend()
    }
