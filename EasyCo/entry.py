import pathlib
import voluptuous

from . import EasyCoConfig

class MissingType:
    def __repr__(self):
        return 'MISSING'


MISSING = MissingType()


class ConfigEntry:
    def __init__(self, default=MISSING, default_factory=MISSING, validator=MISSING,
                 required=True, description='', key_name=None):

        # can't use both
        if default is not MISSING and default_factory is not MISSING:
            raise ValueError('cannot specify both default and default_factory')

        self.default = default
        self.default_factory = default_factory
        self.validator = validator

        assert isinstance(description, str), type(description)
        assert isinstance(required, bool), type(required)

        self.required: bool = required
        self.description: str = description

        self.name = key_name
        self.type = None if self.default is MISSING else type(default)

        # # so we can enter '5' and still get a proper int value
        # if self.value_type is float or self.value_type is int:
        #     self.validator = voluptuous.Coerce(self.value_type)

    def __repr__(self):
        ret = f'<{self.__class__.__name__} '
        for k, v in sorted(self.__dict__.items()):
            ret += f'{k}: {v}, '
        return ret[:-2] + ' >'

    def __key_get_name(self, cfg: EasyCoConfig):
        if cfg.lower_case_keys:
            return self.name.lower()
        return self.name

    def set_validator(self, data: dict, cfg: EasyCoConfig) -> dict:
        assert isinstance(cfg, EasyCoConfig), type(cfg)

        validator = self.validator
        if validator is MISSING:
            if self.type is pathlib.Path:
                validator = str
            else:
                validator = self.type

        key = (voluptuous.Required if self.required else voluptuous.Optional)(
            schema=self.__key_get_name(cfg), description=self.description,
            default=self.default if self.default is not MISSING else voluptuous.UNDEFINED)
        data[key] = validator
        return data

    def set_default(self, data: dict, cfg: EasyCoConfig) -> bool:
        assert isinstance(cfg, EasyCoConfig), type(cfg)

        # skip if we don't have a default value
        if self.default is MISSING and self.default_factory is MISSING:
            return False

        # respect option to only create required keys
        if not self.required and not cfg.create_optional_keys:
            return False

        # value is already there -> do nothing
        name = self.__key_get_name(cfg)
        if name in data:
            return False


        # set default
        data[name] = self.default if self.default is not MISSING else self.default_factory()

        # add description as yaml comment, only set comment if there is none
        if self.description:
            if name not in data.ca.items:
                data.yaml_add_eol_comment(self.description, name)
                # -> only add comments if we add a value, too
                # changed = True

        return True
