""" Tools for validation. """

from jsonmanager.defaults import Defaults
from .rules_validation import validate_rules
from .structure_validation import validate_structure


def validate(*, schema, data, defaults=None):
    if schema is None:
        return

    if defaults is None:
        defaults = Defaults()

    validate_structure(
        schema=schema, data=data, defaults=defaults
        )
    validate_rules(
        schema=schema, data=data, defaults=defaults
        )
