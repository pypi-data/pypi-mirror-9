""" Validate structure of data (types, lists, mappings). """

import itertools

from jsonmanager.exceptions import (
    StructureValidationError,
    ValidationError,
    )
from jsonmanager.schema_types import (
    Dict,
    DictOf,
    ListOf,
    SchemaType,
    )
from jsonmanager import util
from jsonmanager import dispatching
from jsonmanager.dispatching import (
    dispatch,
    )


def validate_structure(schema, data, defaults):
    try:
        dispatch(
            schema=schema,
            data=data,
            location=tuple(),
            defaults=defaults,
            function_map=STRUCTURE_MAP,
            )
    except ValidationError as exc:
        raise StructureValidationError(*exc.errors)


def _validate_scalar_structure(
    schema, data, location, **kwargs # pylint: disable=unused-argument
    ):
    """ `data` must be an instance of `schema` type. """
    if isinstance(data, schema) or data is None:
        return data

    schema_name = '`{}`'.format(schema.__name__)

    _raise_type_validation_error(schema_name, data, location)


def _validate_dict_structure(
    schema,
    data,
    location,
    defaults,
    optional_keys=util.NotSet,
    ignore_extras=util.NotSet,
    **kwargs
    ):
    _confirm_mapping(data, location)

    default_kwargs = defaults.validate_dict_structure_kwargs

    optional_keys = util.resolve_kwarg(
        optional_keys, default_kwargs, 'optional_keys'
        )
    ignore_extras = util.resolve_kwarg(
        ignore_extras, default_kwargs, 'ignore_extras'
        )

    missing_errors = _get_missing_errors(
        schema, data, optional_keys, location
        )

    not_allowed_errors = _get_not_allowed_errors(
        schema, data, ignore_extras, location
        )

    try:
        result = dispatching.utilize_dict_and_capture_errors(
            schema=schema,
            data=data,
            location=location,
            defaults=defaults,
            **kwargs
            )
    except ValidationError as exc:
        captured_errors = exc.errors
    else:
        captured_errors = tuple()

    all_errors = list(
        itertools.chain(missing_errors, not_allowed_errors, captured_errors)
        )

    util.raise_if_errors(all_errors)

    return result


def _get_missing_errors(schema, data, optional_keys, location):
    schema_keys = set(schema.keys())
    data_keys = set(data.keys())

    required_keys = schema_keys - optional_keys
    missing_keys = required_keys - data_keys

    return [
        util.make_error_dict(
            location=location + (key,),
            code='MISSING',
            message='Key missing.',
            data=None
            )
        for key in missing_keys
        ]


def _get_not_allowed_errors(schema, data, ignore_extras, location):
    if ignore_extras:
        return []

    schema_keys = set(schema.keys())
    data_keys = set(data.keys())

    not_allowed_keys = data_keys - schema_keys

    return [
        util.make_error_dict(
            location=location + (key,),
            code='NOT_ALLOWED',
            message='Key not allowed.',
            data=None
            )
        for key in not_allowed_keys
        ]


def _validate_Dict_structure(schema, **kwargs):
    kwargs.update(schema.validate_structure_kwargs)
    return dispatching.utilize_Dict(schema=schema, **kwargs)


def _validate_DictOf_structure(data, location, **kwargs):
    _confirm_mapping(data, location)
    return dispatching.utilize_DictOf(data=data, location=location, **kwargs)


def _validate_list_structure(data, location, defaults, **kwargs):
    _confirm_sequence(data, location)

    kwargs.update(defaults.validate_list_structure_kwargs)

    return dispatching.utilize_list(
        data=data, location=location, defaults=defaults, **kwargs
        )


def _validate_ListOf_structure(data, location, **kwargs):
    _confirm_sequence(data, location)
    return dispatching.utilize_ListOf(
        data=data, location=location, **kwargs
        )


def _confirm_mapping(data, location):
    if util.is_mapping(data):
        return

    _raise_type_validation_error(
        schema_name='mapping', data=data, location=location
        )


def _confirm_sequence(data, location):
    if util.is_sequence(data):
        return

    _raise_type_validation_error(
        schema_name='sequence', data=data, location=location
        )


def _raise_type_validation_error(schema_name, data, location):
    message = 'Expected {expected}; got `{actual}`.'.format(
        expected=schema_name, actual=type(data).__name__
        )

    error_dict = util.make_error_dict(
        location=location, code='TYPE', message=message, data=None
        )

    raise ValidationError(error_dict)


STRUCTURE_MAP = (
    (type, _validate_scalar_structure),
    (tuple, dispatching.utilize_tuple),
    (dict, _validate_dict_structure),
    (Dict, _validate_Dict_structure),
    (DictOf, _validate_DictOf_structure),
    (list, _validate_list_structure),
    (ListOf, _validate_ListOf_structure),
    (SchemaType, dispatching.utilize_SchemaType),
    )
