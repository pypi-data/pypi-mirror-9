import collections

from . import dispatching
from .dispatching import dispatch
from .exceptions import (
    RulesValidationError,
    RuleViolation,
    ValidationError,
    )
from .schema_types import (
    Call,
    DictOf,
    ListOf,
    )
from . import util


def process_input(*, schema, data, default_kwargs=None):
    if default_kwargs is None:
        default_kwargs = {}

    try:
        return dispatch(
            schema=schema,
            data=data,
            location=tuple(),
            default_kwargs=default_kwargs,
            function_map=PROCESS_MAP,
            )
    except ValidationError as exc:
        raise RulesValidationError(*exc.errors)


def _process_Call(
    schema,
    data,
    location,
    default_kwargs,
    **kwargs # pylint: disable=unused-argument
    ):
    function_kwargs = default_kwargs.copy()
    function_kwargs.update(data)
    function_kwargs.update(schema.kwargs)

    try:
        return schema.function(**function_kwargs)
    except RuleViolation as exc:
        util.raise_validation_error_from_rule_violation(exc, location)


def _process_Callable(schema, **kwargs):
    return _process_Call(schema=Call(schema), **kwargs)


PROCESS_MAP = (
    (Call, _process_Call),
    (collections.abc.Callable, _process_Callable),
    (dict, dispatching.utilize_dict_and_capture_errors),
    (DictOf, dispatching.utilize_DictOf),
    (list, dispatching.utilize_list),
    (ListOf, dispatching.utilize_ListOf),
    )
