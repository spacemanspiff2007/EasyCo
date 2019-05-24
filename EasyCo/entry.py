import pathlib
import voluptuous

from . import EasyCoConfig

class MissingType:
    pass
MISSING = MissingType()


class ConfigEntry:
    def __init__(self, default_factory=MISSING, value_type=MISSING, validator=MISSING,
                 required=True, description=None):
        self.value_type = value_type
        self.value_default = default_factory
        self.validator = validator

        assert description is None or isinstance(description, str), type(description)
        assert isinstance(required, bool), type(required)

        self.required: bool = required
        self.description: str = description

        if self.value_default is not MISSING and self.value_type is MISSING:
            self.value_type = type(self.value_default)

        # ---------------------------------------------------------------
        # Custom validators:
        # ---------------------------------------------------------------

        # we load strings and not Path values, in case we modify the value later to a path
        if self.value_type is pathlib.Path:
            self.validator = str
            # self.validator = voluptuous.Coerce(pathlib.Path)

        # # so we can enter '5' and still get a proper int value
        # if self.value_type is float or self.value_type is int:
        #     self.validator = voluptuous.Coerce(self.value_type)

    def __repr__(self):
        ret = f'<{self.__class__.__name__} '
        for k, v in sorted(self.__dict__.items()):
            ret += f'{k}: {v}, '
        return ret[:-2] + ' >'

    def set_validator(self, name: str, data: dict) -> dict:
        key = (voluptuous.Required if self.required else voluptuous.Optional)(
            schema=name, description=self.description,
            default=self.value_default if self.value_default is not MISSING else voluptuous.UNDEFINED)
        data[key] = self.value_type if self.validator is MISSING else self.validator
        return data

    def set_default(self, name: str, data: dict, cfg: EasyCoConfig) -> bool:

        # skip if we don't have a default value
        if self.value_default is MISSING:
            return False

        # respect option to only create required keys
        if not self.required and not cfg.create_optional_keys:
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
