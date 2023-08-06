""" Validate rules (validator functions using `tuple` syntax). """

from jsonmanager.exceptions import (
    RuleViolation,
    RulesValidationError,
    StopValidation,
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


def validate_rules(schema, data, defaults):
    try:
        dispatch(
            schema=schema,
            data=data,
            location=tuple(),
            defaults=defaults,
            function_map=RULES_MAP,
            )
    except ValidationError as exc:
        raise RulesValidationError(*exc.errors)


def _validate_scalar_rules(schema, **kwargs):
    schema_tuple = (schema,)
    _validate_tuple_rules(schema=schema_tuple, **kwargs)


def _validate_tuple_rules(
    schema, data, location, defaults, **kwargs
    ):
    rules = _get_rules(schema, defaults)

    _apply_rules(rules, data, location)

    inner_schema = schema[0]

    if isinstance(inner_schema, type):
        return

    dispatch(
        schema=inner_schema,
        data=data,
        location=location,
        defaults=defaults,
        **kwargs
        )


def _get_rules(schema, defaults):
    rules = schema[1:]

    override_defaults = _get_override_defaults(rules)

    if override_defaults:
        return rules

    return defaults.default_rules + rules


def _get_override_defaults(rules):
    if not rules:
        return False
    return getattr(rules[0], 'override_defaults', False)


def _apply_rules(rules, data, location):
    for rule in rules:
        try:
            rule(data)
        except RuleViolation as exc:
            util.raise_validation_error_from_rule_violation(exc, location)
        except StopValidation:
            break


RULES_MAP = (
    (type, _validate_scalar_rules),
    (tuple, _validate_tuple_rules),
    (dict, dispatching.utilize_dict_and_capture_errors),
    (Dict, dispatching.utilize_Dict),
    (DictOf, dispatching.utilize_DictOf),
    (list, dispatching.utilize_list),
    (ListOf, dispatching.utilize_ListOf),
    (SchemaType, dispatching.utilize_SchemaType),
    )
