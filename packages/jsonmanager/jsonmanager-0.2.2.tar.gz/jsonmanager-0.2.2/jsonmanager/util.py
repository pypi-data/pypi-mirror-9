""" Common tools for both validation and coercion. """

from collections import abc

from .exceptions import (
    SchemaError,
    ValidationError,
    )


NotSet = object()


def select_function(schema, function_map):
    """ Select function from `function_map`, depending on `schema`
        type. """

    for schema_type, processor in function_map:
        if isinstance(schema, schema_type):
            return processor

    raise SchemaError(
        "Unknown schema type: `{}`"
        .format(repr(schema))
        )


def is_mapping(value):
    """ Confirm that `value` is a mapping. """
    return isinstance(value, abc.Mapping)


def is_sequence(value):
    """ Confirm that `value` is a sequence, and not a string. """
    return bool(isinstance(value, abc.Sequence) and not isinstance(value, str))


def raise_if_errors(errors):
    if errors:
        raise ValidationError(*errors)


def raise_validation_error_from_rule_violation(exc, location):
    error_dict = make_error_dict(
        location=location + exc.location,
        code=exc.code,
        message=exc.message,
        data=exc.data,
        )
    raise ValidationError(error_dict)


def make_error_dict(location, code, message, data):
    return {
        'location': location,
        'code': code,
        'message': message,
        'data': data,
        }


def resolve_kwarg(value, default_kwargs, key):
    if value is not NotSet:
        return value

    return default_kwargs[key]
