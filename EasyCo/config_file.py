import unittest, typing, sys, ruamel.yaml, inspect, voluptuous
from pathlib import Path
from copy import deepcopy

import EasyCo

yaml = ruamel.yaml.YAML(typ='rt')
yaml.default_flow_style = False
yaml.default_style = False
yaml.width = 1000000
yaml.allow_unicode = True
yaml.sort_base_mapping_type_on_output = False

class ConfigFile(EasyCo.ConfigContainer):

    def __init__(self, path: Path):
        super().__init__()
        self._path = path.absolute()

    def load(self):

        cfg = {}
        if not self._path.parent.is_dir():
            raise FileNotFoundError(f'Configuration folder {self._path.parent} does not exist!')

        if self._path.is_file():
            with self._path.open('r', encoding='utf-8') as file:
                cfg = yaml.load(file)
            if cfg is None:
                cfg = {}

        # add default values
        changed = self._update_yaml(cfg, insert=False)

        # validate
        schema = {}
        self._update_schema(schema, insert=False)
        schema = voluptuous.Schema(schema)
        cfg = schema(cfg)

        # update optional keys if we have them and write back to disk
        if changed:
            with self._path.open('w', encoding='utf-8') as file:
                yaml.dump(cfg, file)

        self._set_value(cfg)