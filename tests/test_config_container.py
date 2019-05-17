import unittest, voluptuous, ruamel.yaml, io

from EasyCo import ConfigContainer, ConfigEntry


class TestClassSimple(ConfigContainer):
    type_hint_and_value: float = 0
    only_type_hint: int
    only_value = 7.5

    def function_b(self) -> bool:
        pass

class test_configfile(unittest.TestCase):

    def test_schema(self):
        ist = {}
        TestClassSimple()._update_schema(ist)
        soll = {'TestClassSimple': {
            voluptuous.Required('type_hint_and_value', default=0): float,
            voluptuous.Required('only_type_hint'): int,
            voluptuous.Required('only_value', default=7.5): float,
        }}
        self.assertDictEqual(ist, soll)

    def test_defaults_creation(self):
        data = {}
        TestClassSimple()._update_yaml(data)
        self.assertDictEqual(data, {'TestClassSimple': {
            'type_hint_and_value' : 0,
            'only_value' : 7.5
        }})

    def test_defaults_update(self):
        data = {'TestClassSimple': {'only_value' : 999.999}}
        TestClassSimple()._update_yaml(data)
        self.assertDictEqual(data, {'TestClassSimple': {
            'type_hint_and_value' : 0,
            'only_value' : 999.999
        }})

    def test_comments(self):
        class A(ConfigContainer):
            asdf = ConfigEntry(default_value=123456789, description='Test Comment')
            bcdf = ConfigEntry(default_value='asdf', description='Test 123')

        data = {}
        A()._update_yaml(data)

        tmp = io.StringIO()
        ruamel.yaml.YAML().dump(data, tmp)
        output = tmp.getvalue()

        self.assertEqual(output, 'A:\n  asdf: 123456789  # Test Comment\n  bcdf: asdf # Test 123\n')

    def test_container_in_container(self):

        class A(ConfigContainer):
            asdf = ConfigEntry(default_value=123456789, description='Test Comment')
            bcdf = ConfigEntry(default_value='asdf', description='Test 123')
            simple = TestClassSimple()

        ist = {}
        test = A()
        test._update_schema(ist)
        soll = { 'A':{
            voluptuous.Required('asdf', default=123456789): int,
            voluptuous.Required('bcdf', default='asdf'): str,

            'TestClassSimple': {
                voluptuous.Required('type_hint_and_value', default=0): float,
                voluptuous.Required('only_type_hint'): int,
                voluptuous.Required('only_value', default=7.5): float,
            }
        }}

        self.assertDictEqual(ist, soll)

        data = {}
        A()._update_yaml(data)

        tmp = io.StringIO()
        ruamel.yaml.YAML().dump(data, tmp)
        output = tmp.getvalue()

        self.assertEqual(output, '''A:
  asdf: 123456789  # Test Comment
  bcdf: asdf # Test 123
  TestClassSimple:
    type_hint_and_value: 0
    only_value: 7.5\n''')


if __name__ == "__main__":
    import logging, sys
    _log = logging.getLogger()
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(logging.Formatter("[{asctime:s}] [{name:25s}] {levelname:8s} | {message:s}", style='{'))
    _log.addHandler(ch)

    unittest.main()

