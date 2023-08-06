class Defaults:
    def __init__(
        self,
        default_rules=tuple(),
        dict_optional_keys=tuple(),
        dict_ignore_extras=False,
        dict_strip_extras=False,
        list_ignore_extras=False,
        list_strip_extras=False,
        ):
        if default_rules is None:
            default_rules = tuple()

        if dict_strip_extras is True:
            dict_ignore_extras = True

        if list_strip_extras is True:
            list_ignore_extras = True

        self.default_rules = default_rules

        dict_optional_keys_set = set(dict_optional_keys)

        self.validate_dict_structure_kwargs = dict(
            optional_keys=dict_optional_keys_set,
            ignore_extras=dict_ignore_extras,
            )

        self.validate_list_structure_kwargs = dict(
            optional_keys=set(),
            ignore_extras=list_ignore_extras,
            )

        self.render_dict_kwargs = dict(
            strip_extras=dict_strip_extras,
            )

        self.render_list_kwargs = dict(
            strip_extras=list_strip_extras,
            )
