from .defaults import (
    Defaults,
    )
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
from . import util


def render(*, schema, data, defaults=None):
    if schema is None:
        return data

    if defaults is None:
        defaults = Defaults()

    return dispatch(
        schema=schema,
        data=data,
        defaults=defaults,
        function_map=RENDER_MAP,
        )


def _render_dict(schema, data, defaults, strip_extras=util.NotSet, **kwargs):
    default_kwargs = defaults.render_dict_kwargs

    strip_extras = util.resolve_kwarg(
        strip_extras, default_kwargs, 'strip_extras'
        )

    resolved_data = _resolve_data_dict(schema, data, strip_extras)

    return dispatching.utilize_dict_simple(
        schema=schema,
        data=resolved_data,
        defaults=defaults,
        **kwargs
        )


def _resolve_data_dict(schema, data, strip_extras):
    if not strip_extras:
        return data

    actual_keys = set(schema.keys()) & set(data.keys())

    return {
        key: value
        for key, value in data.items()
        if key in actual_keys
        }


def _render_Dict(schema, **kwargs):
    kwargs.update(schema.render_kwargs)
    return dispatching.utilize_Dict(schema=schema, **kwargs)


def _render_list(defaults, **kwargs):
    kwargs.update(defaults.render_list_kwargs)
    return dispatching.utilize_list(defaults=defaults, **kwargs)


RENDER_MAP = [
    (type, dispatching.return_data_unchanged),
    (tuple, dispatching.utilize_tuple),
    (dict, _render_dict),
    (Dict, _render_Dict),
    (DictOf, dispatching.utilize_DictOf),
    (list, _render_list),
    (ListOf, dispatching.utilize_ListOf),
    (SchemaType, dispatching.schema_type_dispatcher('render')),
    ]
