import voluptuous, ruamel.yaml


class ValueNotConfigured:
    pass


class ConfigEntry:
    def __init__(self, default_value=ValueNotConfigured, value_type=ValueNotConfigured, validator=ValueNotConfigured,
                  required=False, description=None):
        self.value_type = value_type
        self.value_default = default_value
        self.validator = validator

        assert description is None or isinstance(description, str), type(description)
        assert isinstance(required, bool), type(required)

        self.required: bool = required
        self.description: str = description

        if self.value_default is not ValueNotConfigured and self.value_type is ValueNotConfigured:
            self.value_type = type(self.value_default)

    def __repr__(self):
        ret = f'<{self.__class__.__name__} '
        for k, v in sorted(self.__dict__.items()):
            ret += f'{k}: {v}, '
        return ret[:-2] + ' >'

    def set_validator(self, name: str, data: dict):
        key =(voluptuous.Required if self.required else voluptuous.Optional) \
             (schema=name, description=self.description,
              default=self.value_default if self.value_default is not ValueNotConfigured else voluptuous.UNDEFINED)
        data[key] = self.value_type if self.validator is ValueNotConfigured else self.validator

    def set_default(self, name: str, data: dict) -> bool:

        # skip if we don't have a default value
        if self.value_default is ValueNotConfigured:
            return False

        changed = False

        # don't override already existing values
        if name not in data:
            data[name] = self.value_default
            changed = True

        # add description as yaml comment, only set comment if there is none
        if self.description is not None:
            if name not in data.ca.items:
                data.yaml_add_eol_comment(self.description, name)
                # -> only add comments if we add a value, too
                # changed = True

        return changed
