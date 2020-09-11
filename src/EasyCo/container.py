import inspect
import typing

import ruamel.yaml  # type: ignore

from . import ConfigEntry, EasyCoConfig, DEFAULT_CONFIGURATION
from .entry import MISSING, SKIP


class ConfigContainer:

    def __init__(self, key_name: typing.Optional[str] = None):
        super().__init__()

        self.__container_name: typing.Optional[str] = key_name
        self.__cfg = DEFAULT_CONFIGURATION
        self.__notify = []
        self.__entries: typing.Dict[str, ConfigEntry] = {}
        self.__containers: typing.Dict[str, ConfigContainer] = {}

        annotations = self.__class__.__dict__.get('__annotations__', {})
        for a_name, a_type in annotations.items():
            default_value = getattr(self.__class__, a_name, MISSING)

            # Make it possible to skip values
            if default_value is SKIP:
                continue

            if isinstance(default_value, ConfigEntry):
                entry = default_value
            else:
                entry = ConfigEntry(default=default_value)

            entry.set_type_hint(a_name, a_type)
            self.__entries[a_name] = entry

            if isinstance(entry.default, (list, dict, set)):
                raise ValueError(f'mutable default {type(entry.default)} for field '
                                 f'{entry.name} is not allowed: use default_factory')

        # find inherited stuff
        for name, obj in inspect.getmembers(self):
            if isinstance(obj, ConfigContainer):
                self.__containers[name] = obj
            elif isinstance(obj, ConfigEntry):
                if name not in self.__entries:
                    self.__entries[name] = obj
                # check that the user did not forget the type
                if obj.type is None:
                    raise ValueError(f'missing type hint for entry "{name}"!')
            elif isinstance(obj, EasyCoConfig):
                self.__cfg = obj

        for cfg in self.__containers.values():
            cfg._set_config(self.__cfg)

    def on_set_value(self, var_name: str, new_value):
        """Override this function to perform datatype conversions when values get loaded from the file

        :param var_name: variable name
        :param new_value: new value which was loaded from file
        :return: Value which will be set
        """
        return new_value

    def on_all_values_set(self):
        """Override this function. It'll be called when all values from the file have been correctly set.
        Use it e.g. to calculate and set additional variables.
        """
        return None

    def subscribe_for_changes(self, func):
        """When a value in this container changes the passed function will be called.

        :param func: function which will be called
        """
        if func not in self.__notify:
            self.__notify.append(func)

    def _call_container_funcs(self, func_name: str, *args, **kwargs):

        for name, obj in self.__containers.items():
            assert isinstance(obj, ConfigContainer)

            # call child funcs before we set the value
            obj._call_container_funcs(func_name, *args, **kwargs)

        # call function if it exists
        func = getattr(self, func_name, None)
        if func is not None:
            func(*args, **kwargs)

    def __get_container_name(self, obj) -> str:
        assert isinstance(obj, ConfigContainer), type(obj)
        key_name = obj.__class__.__name__ if self.__container_name is None else self.__container_name
        if self.__cfg.lower_case_keys:
            key_name = key_name.lower()
        return key_name

    def _set_config(self, cfg):
        assert isinstance(cfg, EasyCoConfig)
        if self.__cfg is DEFAULT_CONFIGURATION:
            self.__cfg = cfg

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

    def _update_schema(self, schema, insert_values=True):
        assert isinstance(insert_values, bool)

        if insert_values:
            schema[self.__get_container_name(self)] = insert = {}
        else:
            insert = schema

        for name, entry in self.__entries.items():
            entry.set_validator(insert, self.__cfg)

        for container in self.__containers.values():
            container._update_schema(insert)

        return None

    def _update_yaml(self, data, insert_values=True) -> int:
        assert isinstance(insert_values, bool)

        if insert_values:
            insert = data.setdefault(self.__get_container_name(self), ruamel.yaml.comments.CommentedMap())
        else:
            insert = data

        changed = 0
        for name, entry in self.__entries.items():
            changed += entry.set_default(insert, self.__cfg)

        for container in self.__containers.values():
            changed += container._update_yaml(insert)

        return changed

    def _set_value(self, data) -> int:

        # process values in container
        value_changed = 0
        for name, obj in self.__entries.items():
            try:
                value_new = data[obj.get_key_name(self.__cfg)]
            except KeyError:
                continue

            value_new = self.on_set_value(name, value_new)
            value_cur = getattr(self, name, None)
            if value_cur != value_new:
                setattr(self, name, value_new)
                value_changed += 1

        # Process all subcontainers
        container_changed = 0
        for container in self.__containers.values():
            try:
                container_data = data[self.__get_container_name(container)]
            except KeyError:
                continue

            container_changed += container._set_value(container_data)

        # we have set all values in this container and subcontainer
        self.on_all_values_set()

        # notify all subscribers that a value has changed
        if value_changed or container_changed:
            self._notify()

        return value_changed + container_changed
