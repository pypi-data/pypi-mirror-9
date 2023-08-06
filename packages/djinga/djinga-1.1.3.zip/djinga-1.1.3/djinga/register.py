from functools import partial


def _add_attrs(func, jjattr, name=None):
    setattr(func, '_jj_%s' % jjattr, True)
    func._jj_name = name or func.__name__
    return func


def _jj_decorator(jjattr, *args):
    if isinstance(args[0], basestring):
        name = args[0]
        return partial(_add_attrs(jjattr=jjattr, name=name))
    else:
        return _add_attrs(args[0], jjattr)


def jj_filter(*args):
    return _jj_decorator('filter', *args)


def jj_global(*args):
    return _jj_decorator('global', *args)
