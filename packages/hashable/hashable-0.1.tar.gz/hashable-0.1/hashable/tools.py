from operator import attrgetter, methodcaller


def create_getters_list(attributes=None, methods=None):
    getters_list = []
    if attributes is not None:
        getters_list.extend(map(attrgetter, attributes))
    if methods is not None:
        getters_list.extend(map(methodcaller, methods))
    return getters_list


def get_super_not_buildin_method_or_none(obj, name):
    method = getattr(obj, name, None)
    if method is None:
        return None
    if isinstance(method, build_in_methods_types):
        return None
    return method


class _C(object):
    pass
build_in_methods_types = (type(_C.__eq__), type(_C.__hash__))
del _C
