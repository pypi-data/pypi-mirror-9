from jsonmanager.coercion_tools import coerce
from jsonmanager.render_tools import render
from jsonmanager.validation_tools import validate


def manage_input(schema, data, defaults=None, manager=None):
    coerced_data = coerce(schema=schema, data=data, manager=manager)
    validate(schema=schema, data=coerced_data, defaults=defaults)
    return render(schema=schema, data=coerced_data, defaults=defaults)
