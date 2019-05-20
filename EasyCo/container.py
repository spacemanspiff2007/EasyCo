import inspect
import ruamel.yaml
import typing

from . import ConfigEntry


class ConfigContainer:

    def __init__(self):
        super().__init__()
        annotations = self.__class__.__dict__.get('__annotations__', {})
        declared = {k: v for k, v in self.__class__.__dict__.items()
                    if not k.startswith('_') and not inspect.isfunction(v) and not isinstance(v, ConfigContainer)}

        self.__entries: typing.Dict[str, ConfigEntry] = {}
        self.__container: typing.Dict[str, ConfigContainer] = {name : obj for name, obj in inspect.getmembers(self)
                                                               if isinstance(obj, ConfigContainer)}

        # find ConfigEntry in inherited classes
        for name, obj in inspect.getmembers(self):
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
            self.__entries[name] = ConfigEntry(value_type=value_type, default_value=value)

        for name, value_type in annotations.items():
            # we have already processed this
            if name in declared:
                continue

            self.__entries[name] = ConfigEntry(value_type=value_type, required=False)

        # notify functions
        self.__notify = []

    def subscribe_for_changes(self, func):
        if func not in self.__notify:
            self.__notify.append(func)

    def _notify(self):
        for func in self.__notify:
            try:
                func()
            except Exception:
                pass

    def _update_schema(self, schema, insert=True):
        if insert:
            schema[self.__class__.__name__] = insert = {}
        else:
            insert = schema

        for name, entry in self.__entries.items():
            entry.set_validator(name, insert)

        for container in self.__container.values():
            container._update_schema(insert)

        return None

    def _update_yaml(self, data, insert=True) -> int:
        if insert:
            node_name = self.__class__.__name__
            insert = data.setdefault(node_name, ruamel.yaml.comments.CommentedMap())
        else:
            insert = data

        changed = 0
        for name, entry in self.__entries.items():
            changed += entry.set_default(name, insert)

        for container in self.__container.values():
            changed += container._update_yaml(insert)

        return changed

    def _set_value(self, data) -> int:
        changed = 0
        for name, obj in self.__entries.items():
            value_cur = getattr(self, name, None)
            value_new = data[name]
            if value_cur != value_new:
                setattr(self, name, value_new)
                changed += 1

        for container in self.__container.values():
            changed += container._set_value(data[container.__class__.__name__])

        return changed
