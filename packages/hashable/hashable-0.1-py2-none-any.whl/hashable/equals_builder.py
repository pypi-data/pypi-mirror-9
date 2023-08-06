from .tools import create_getters_list, get_super_not_buildin_method_or_none


__all__ = ['EqualsBuilder']


class EqualsBuilderState(object):
    def __init__(self, builder):
        self.builder = builder


class ZeroCheck(EqualsBuilderState):
    def append(self, this, other):
        pass


class Comparator(EqualsBuilderState):
    def append(self, this, other):
        if this is not other and this != other:
            self.builder._mark_as_different()


class EqualsBuilder(object):
    _same_instances = False
    _type_check_failed = False

    @classmethod
    def auto_generate(cls, eq_cls, attributes=None, methods=None):
        getters_list = create_getters_list(attributes, methods)

        super_method = get_super_not_buildin_method_or_none(eq_cls, '__eq__')

        def __eq__(self, other):
            eq = cls(self, other)
            if eq.is_type_check_failed():
                return False
            if eq.is_same_instances():
                return True

            if super_method is not None:
                eq.append_super(super_method(self, other))

            for getter in getters_list:
                self_val = getter(self)
                other_val = getter(other)
                eq.append(self_val, other_val)
            return eq.is_equals()
        return __eq__

    @classmethod
    def auto_ne_from_eq(cls):
        def __ne__(self, other):
            return not self == other
        return __ne__

    def __init__(self, this, other):
        if this is other:
            self._same_instances = True
            self._equals = True
            self._state = ZeroCheck(self)
        elif type(this) != type(other):
            self._type_check_failed = True
            self._mark_as_different()
        else:
            self._equals = True
            self._state = Comparator(self)

    def is_type_check_failed(self):
        return self._type_check_failed

    def is_same_instances(self):
        return self._same_instances

    def append_super(self, super_is_equals):
        if self._equals and not super_is_equals:
            self._mark_as_different()
        return self

    def append(self, this, other):
        self._state.append(this, other)
        return self

    def is_equals(self):
        return self._equals

    def _mark_as_different(self):
        self._equals = False
        self._state = ZeroCheck(self)
