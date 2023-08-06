""" Special types for schemas. """

import collections


_NotSet = object()


AnyType = object


class DictOf:
    """ A dictionary with arbitrary keys. All values must conform to `schema`.
        """
    def __init__(self, schema):
        self.schema = schema


class ListOf:
    """ A list with arbitrary length. All values must conform to `schema`. """
    def __init__(self, schema):
        self.schema = schema


class Dict:
    def __init__(
        self,
        schema,
        *,
        optional_keys=_NotSet,
        ignore_extras=_NotSet,
        strip_extras=_NotSet
        ):
        self.schema = schema

        if optional_keys is not _NotSet:
            optional_keys = set(optional_keys)

        if strip_extras is True:
            ignore_extras = True

        self.validate_structure_kwargs = {
            key: value
            for key, value in [
                ('optional_keys', optional_keys),
                ('ignore_extras', ignore_extras),
                ]
            if value is not _NotSet
            }

        self.render_kwargs = {
            key: value
            for key, value in [
                ('strip_extras', strip_extras),
                ]
            if value is not _NotSet
            }


class Call:
    def __init__(self, function, **kwargs):
        self.function = function
        self.kwargs = kwargs


class SchemaType:
    """ Parent class for user-defined schema types. """

    schema = object

    recursive_coerce = False
    recursive_render = False


class MapList(SchemaType):
    """ Renders to a dictionary. Keys can be any type, rather than just strings.

        Input data is a list of dictionaries like this:

            [
                {'key': some_key, 'value': some_value},
                ...
                ]

        Rendered result is a dictionary like this:

            {
                some_key: some_value,
                ...
                }
        """

    def __init__(self, *, key, value):
        self.key_schema = key
        self.value_schema = value

    @staticmethod
    def render(data):
        return collections.OrderedDict(
            (item['key'], item['value'])
            for item in data
            )

    @property
    def schema(self):
        return ListOf(
            {
                'key': self.key_schema,
                'value': self.value_schema,
                }
            )

    recursive_render = True
