import inspect
import ruamel.yaml
import typing

from . import ConfigEntry, EasyCoConfig, DEFAULT_CONFIGURATION


class ConfigContainer:

    def __init__(self):
        super().__init__()
        annotations = self.__class__.__dict__.get('__annotations__', {})
        declared = {k: v for k, v in self.__class__.__dict__.items()
                    if not k.startswith(f'_') and not inspect.isfunction(v) and not isinstance(v, (ConfigContainer,
                                                                                                   EasyCoConfig))}

        self.__cfg: EasyCoConfig = DEFAULT_CONFIGURATION
        self.__entries: typing.Dict[str, ConfigEntry] = {}
        self.__container: typing.Dict[str, ConfigContainer] = {name : obj for name, obj in inspect.getmembers(self)
                                                               if isinstance(obj, ConfigContainer)}

        self.__container: typing.Dict[str, ConfigContainer] = {}

        self.__find_create_config_containers()

        # find ConfigEntry in inherited classes
        for name, obj in inspect.getmembers(self):
            # configuration for the current container
            if isinstance(obj, EasyCoConfig):
                self.__cfg = obj
                continue

            if not isinstance(obj, ConfigEntry):
                continue
            if name in declared:
                continue
            declared[name] = obj

        for name, value in declared.items():
            # we already have the correct values
            if isinstance(value, ConfigEntry):
                self.__entries[name] = value
                continue

            # create them ourselves
            value_type = annotations.get(name, type(value))
            self.__entries[name] = ConfigEntry(
                value_type=self.get_value_validator(name, value_type), default_factory=value)

        for name, value_type in annotations.items():
            # we have already processed this
            if name in declared:
                continue

            self.__entries[name] = ConfigEntry(value_type=self.get_value_validator(name, value_type), required=False)

        # notify functions
        self.__notify = []

        # set parent_configuration
        for container in self.__container.values():
            container._set_config(self.__cfg)

    def __find_create_config_containers(self) :
        for name, obj in inspect.getmembers(self.__class__):
            if not isinstance(obj, ConfigContainer):
                continue

            self.__container[name] = obj

    def __find_declared_variables(self) -> dict:
        ret = {}
        for k, v in self.__class__.__dict__.items():
            if k.startswith('_'):
                continue
            if inspect.isfunction(v):
                continue
            if isinstance(v, (EasyCoConfig, ConfigContainer)):
                continue
            if inspect.isclass(v):
                continue
            ret[k] = v
        return ret



    def get_value_validator(self, var_name: str, var_type):
        return var_type

    def set_value_from_file(self, var_name: str, new_value):
        return new_value

    def subscribe_for_changes(self, func):
        if func not in self.__notify:
            self.__notify.append(func)

    def _set_config(self, cfg):
        assert isinstance(cfg, EasyCoConfig)
        if self.__cfg is DEFAULT_CONFIGURATION:
            self.__cfg = cfg

    def __get_container_name(self, obj) -> str:
        assert isinstance(obj, ConfigContainer), type(obj)
        key_name = obj.__class__.__name__
        if self.__cfg.lower_case_keys:
            key_name = key_name.lower()
        return key_name

    def __get_key_name(self, name: str) -> str:
        assert isinstance(name, str), type(name)
        if self.__cfg.lower_case_keys:
            name = name.lower()
        return name

    def _notify(self):
        for func in self.__notify:
            try:
                func()
            except Exception:
                pass

    def _update_schema(self, schema, insert=True):
        if insert:
            schema[self.__get_container_name(self)] = insert = {}
        else:
            insert = schema

        for name, entry in self.__entries.items():
            entry.set_validator(self.__get_key_name(name), insert)

        for container in self.__container.values():
            container._update_schema(insert)

        return None

    def _update_yaml(self, data, insert=True) -> int:
        if insert:
            insert = data.setdefault(self.__get_container_name(self), ruamel.yaml.comments.CommentedMap())
        else:
            insert = data

        changed = 0
        for name, entry in self.__entries.items():
            changed += entry.set_default(self.__get_key_name(name), insert, self.__cfg)

        for container in self.__container.values():
            changed += container._update_yaml(insert)

        return changed

    def _set_value(self, data) -> int:
        value_changed = 0
        for name, obj in self.__entries.items():
            try:
                value_new = data[self.__get_key_name(name)]
            except KeyError:
                continue

            value_new = self.set_value_from_file(name, value_new)
            value_cur = getattr(self, name, None)
            if value_cur != value_new:
                setattr(self, name, value_new)
                value_changed += 1

        container_changed = 0
        for container in self.__container.values():
            try:
                container_data = data[self.__get_container_name(container)]
            except KeyError:
                continue

            container_changed += container._set_value(container_data)

        # notify all subscribers that a value has changed
        if value_changed or container_changed:
            self._notify()

        return value_changed + container_changed



