""" Tools for calling mapped functions. """

import collections
import itertools

from .exceptions import (
    ValidationError,
    )
from .schema_types import (
    SchemaType,
    )
from . import util


_NoSchema = object()


def dispatch(schema, function_map, **kwargs):
    """ Call the appropriate function, depending on `schema` type. """

    if isinstance(schema, type):
        if issubclass(schema, SchemaType):
            schema = schema()

    function = util.select_function(schema, function_map)
    return function(
        schema=schema, function_map=function_map, **kwargs
        )


def return_data_unchanged(data, **kwargs): # pylint: disable=unused-argument
    return data


def utilize_dict_simple(schema, data, **kwargs):
    """ Dispatch each item in `data` with a corresponding item in `schema`.
        Return extra items from `data` unchanged.
        Return value is a `dict` instance. """
    schema_keys = set(schema.keys())
    data_keys = set(data.keys())

    dispatched_items = [
        (key, dispatch(schema=schema[key], data=data[key], **kwargs))
        for key in data_keys & schema_keys
        ]

    # Items from `data` with no corresponding key in `schema`.
    extra_items = [
        (key, data[key])
        for key in data_keys - schema_keys
        ]

    return dict(dispatched_items + extra_items)


def utilize_dict_and_capture_errors(schema, data, location, **kwargs):
    """ Dispatch each item in `data` with a corresponding item in `schema`.
        Capture all errors raised during dispatch. If any errors were captured,
            raise `ValidationError` which includes all captured errors.
        Extra items from `data` are returned unchanged. """

    result_items, captured_error_lists = (
        _get_all_result_items_and_capture_errors(
            schema, data, location, **kwargs
            )
        )

    errors = list(itertools.chain(*captured_error_lists))

    util.raise_if_errors(errors)

    return dict(result_items)


def _get_all_result_items_and_capture_errors(schema, data, location, **kwargs):
    result = tuple(zip(*[
        _get_one_result_item_and_capture_errors(
            schema=schema.get(key, _NoSchema),
            data=data[key],
            location=location + (key,),
            key=key,
            **kwargs
            )
        for key in data.keys()
        ]))

    if not result:
        return tuple([tuple(), tuple()])

    return result


def _get_one_result_item_and_capture_errors(schema, data, key, **kwargs):
    if schema is _NoSchema:
        return (key, data), tuple()

    try:
        validated_data = dispatch(schema=schema, data=data, **kwargs)
    except ValidationError as exc:
        return (key, None), exc.errors

    return (key, validated_data), tuple()


def utilize_Dict(schema, **kwargs):
    return dispatch(schema=schema.schema, **kwargs)


def utilize_DictOf(schema, data, **kwargs):
    """ Validate a dictionary with arbitrary keys.
        Validate each value from `data` against `schema.schema`.
        `schema` is a `DictOf` instance. """

    schema_dict = {key: schema.schema for key in data.keys()}

    return dispatch(schema=schema_dict, data=data, **kwargs)


def utilize_list(schema, data, **kwargs):
    """ Validate a list.
        Validate each value from `data` against the corresponding `schema`
        value.
        `schema` and `data` must have the same length. """

    schema_dict = _make_dict_from_list(schema)
    data_dict = _make_dict_from_list(data)

    result_dict = dispatch(schema=schema_dict, data=data_dict, **kwargs)

    return _make_list_from_dict(result_dict)


def _make_dict_from_list(input_list):
    return collections.OrderedDict(enumerate(input_list))


def _make_list_from_dict(result_dict):
    return [value for key, value in sorted(result_dict.items())]


def utilize_ListOf(schema, data, **kwargs):
    """ Validate a list with arbitrary length.
        Validate each value from `data` against `schema.schema`.
        `schema` is a `ListOf` instance. """
    schema_list = [schema.schema for item in data]

    return utilize_list(schema=schema_list, data=data, **kwargs)


def utilize_tuple(schema, **kwargs):
    """ The 0-index element of `schema` is the actual schema object.
        The rest of the elements in `schema` are validator functions. """
    return dispatch(schema=schema[0], **kwargs)


def utilize_SchemaType(schema, **kwargs):
    return dispatch(schema=schema.schema, **kwargs)


def schema_type_dispatcher(method_name):

    def dispatcher_function(schema, data, **kwargs):
        if not hasattr(schema, method_name):
            return dispatch(schema=schema.schema, data=data, **kwargs)

        if getattr(schema, 'recursive_' + method_name):
            pre_dispatched_data = dispatch(
                schema=schema.schema, data=data, **kwargs
                )
        else:
            pre_dispatched_data = data

        method = getattr(schema, method_name)
        return method(data=pre_dispatched_data)

    return dispatcher_function
