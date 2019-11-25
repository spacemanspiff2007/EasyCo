import typing
from pathlib import Path

import ruamel.yaml
import voluptuous

import EasyCo

yaml = ruamel.yaml.YAML(typ='rt')
yaml.default_flow_style = False
yaml.default_style = False
yaml.width = 1000000
yaml.allow_unicode = True
yaml.sort_base_mapping_type_on_output = False


class ConfigFile(EasyCo.ConfigContainer):

    def __init__(self, path: Path = None):
        super().__init__()
        if path is not None:
            self.set_path(path)

    def set_path(self, path: typing.Union[Path, str]):
        """Set the path to the configuration file.
        If no file extension is specified ``.yml`` will be automatically appended.

        :param path: Path obj or str
        """
        if isinstance(path, str):
            path = Path(path)
        assert isinstance(path, Path), type(path)

        self._path = path.resolve()
        if self._path.suffix == '':
            self._path = self._path.with_name(self._path.name + '.yml')

        # set default path for all file containers
        self._call_container_funcs('_set_default_path', self._path.parent)

    def load(self, path_or_stream: typing.Union[Path, typing.TextIO] = None) -> 'ConfigFile':
        """Load values from the configuration file. If the file doesn't exist it will be created.
        Missing required config entries will also be created.

        :param path_or_stream: if not already set a path instance to the config file or
                               a file like obj (opened in text mode 'rw')
        """
        cfg = ruamel.yaml.comments.CommentedMap()

        if isinstance(path_or_stream, Path) or path_or_stream is None:
            if path_or_stream is not None:
                self.set_path(path_or_stream)
            try:
                with self._path.open('r', encoding='utf-8') as file:
                    cfg = yaml.load(file)
            except FileNotFoundError:
                pass
        else:
            # load from file obj
            cfg = yaml.load(path_or_stream)

        # If the file is empty we get None instead of the Commented Map
        if cfg is None:
            cfg = ruamel.yaml.comments.CommentedMap()


        # add default values
        data_changed = self._update_yaml(cfg, insert_values=False)

        # validate - this also makes it a normal dict
        schema = {}
        self._update_schema(schema, insert_values=False)
        schema = voluptuous.Schema(schema)
        validated_cfg = schema(cfg)

        # update optional keys if we have them and write back to disk
        if data_changed:
            # Check if we can create the file
            if isinstance(path_or_stream, Path) or path_or_stream is None:
                if not self._path.parent.is_dir():
                    raise FileNotFoundError(f'Specified configuration folder {self._path.parent} does not exist!')
                with self._path.open('w', encoding='utf-8') as file:
                    yaml.dump(cfg, file)
            else:
                path_or_stream.seek(0)
                yaml.dump(cfg, path_or_stream)

        self._set_value(validated_cfg)
        return self
