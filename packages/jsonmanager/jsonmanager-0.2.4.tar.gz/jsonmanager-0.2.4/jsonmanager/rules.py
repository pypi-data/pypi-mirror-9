import re

from .exceptions import (
    RuleViolation,
    StopValidation,
    )


def override_defaults(rule):
    rule.override_defaults = True
    return rule


@override_defaults
def Required(data):
    if data is None or data == '':
        raise RuleViolation(code='required', message='Required value.')


@override_defaults
def Nullable(data):
    if data is None:
        raise StopValidation


@override_defaults
def NoDefaults(data): # pylint: disable=unused-argument
    pass


class Length:
    """ `data` must have the specified length. """

    def __init__(self, length):
        self.length = length

    def __call__(self, data):
        if len(data) == self.length:
            return

        raise RuleViolation(
            code='length',
            message='Invalid length.',
            data={'length': self.length}
            )


class OneOf:
    """ `data` must be a member of `collection`. """

    def __init__(self, *collection):
        self.collection = collection

    def __call__(self, data):
        if data in self.collection:
            return

        raise RuleViolation(
            code='one_of',
            message='Not a member of the approved collection.',
            data={'collection': [str(item) for item in self.collection]}
            )


class Range:
    """ `data` must be with specified range. """

    def __init__(self, minimum, maximum):
        self.min = minimum
        self.max = maximum

    def __call__(self, data):
        if self.min <= data <= self.max:
            return

        raise RuleViolation(
            code='range',
            message='Not within expected range.',
            data={
                'min': self.min,
                'max': self.max
                }
            )


class Regex:
    """ `data` must match regular expression. """

    def __init__(self, pattern):
        self.pattern = pattern

    def __call__(self, data):
        if re.match(self.pattern, data):
            return

        raise RuleViolation(
            code='regex',
            message='Does not match expected pattern.',
            data={'regex': self.pattern}
            )
