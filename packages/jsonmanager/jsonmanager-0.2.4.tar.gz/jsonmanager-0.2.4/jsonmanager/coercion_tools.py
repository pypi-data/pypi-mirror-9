""" Tools for coercion. """
import inspect

from . import dispatching
from .dispatching import (
    dispatch,
    )
from .schema_types import (
    Dict,
    DictOf,
    ListOf,
    SchemaType,
    )
from .util import (
    is_mapping,
    is_sequence,
    )


class CoercionManagerBase:
    """ Contains coercion methods.

        To declare a coercion method, decorate a method like this:

            @coercion_method(SomeType)
            def coerce_some_type(self, data):
                ... do coercion here ...
                return coerced_value
        """

    def __init__(self):
        self._coercion_methods = {}
        for _, method in inspect.getmembers(self):
            if not hasattr(method, 'coercion_types'):
                continue
            for coercion_type in method.coercion_types:
                self._coercion_methods[coercion_type] = method

    def coerce(self, *, schema, data):
        """ Coerce input data. """
        return coerce(schema=schema, data=data, manager=self)

    def coerce_data(self, schema, data):
        """ Get the appropriate coercion method from `self`, depending on
            `schema`.
            If no coercion method found, return `data` unchanged. """
        method = self._coercion_methods.get(schema, None)

        if method is None:
            return data

        return method(data)


def coercion_method(coercion_type):
    def prepared_decorator(method):
        _apply_coercion_type(method, coercion_type)
        return method
    return prepared_decorator


def coercion_staticmethod(coercion_type):
    def prepared_decorator(method):
        _apply_coercion_type(method, coercion_type)
        return staticmethod(method)
    return prepared_decorator


def _apply_coercion_type(method, coercion_type):
    if not hasattr(method, 'coercion_types'):
        method.coercion_types = []
    method.coercion_types.append(coercion_type)


def coerce(*, schema, data, manager=None):
    if schema is None:
        return data

    if manager is None:
        manager = CoercionManagerBase()

    return dispatch(
        schema=schema,
        data=data,
        manager=manager,
        function_map=COERCION_MAP,
        )


def _coerce_scalar(
    schema, data, manager, **kwargs # pylint: disable=unused-argument
    ):
    return manager.coerce_data(schema, data)


def _coercion_function(data_check, utilize_function):
    def function(data, **kwargs):
        if not data_check(data):
            return data

        return utilize_function(data=data, **kwargs)

    return function


_coerce_dict = _coercion_function(is_mapping, dispatching.utilize_dict_simple)
_coerce_DictOf = _coercion_function(is_mapping, dispatching.utilize_DictOf)
_coerce_list = _coercion_function(is_sequence, dispatching.utilize_list)
_coerce_ListOf = _coercion_function(is_sequence, dispatching.utilize_ListOf)


COERCION_MAP = [
    (type, _coerce_scalar),
    (tuple, dispatching.utilize_tuple),
    (dict, _coerce_dict),
    (Dict, dispatching.utilize_Dict),
    (DictOf, _coerce_DictOf),
    (list, _coerce_list),
    (ListOf, _coerce_ListOf),
    (SchemaType, dispatching.schema_type_dispatcher('coerce'))
    ]
