import unittest
import voluptuous

from EasyCo import ConfigContainer


class Test1(ConfigContainer):
    type_hint_and_value: float = 0
    only_type_hint: int
    only_value = 7.5


class Test2(ConfigContainer):
    type_hint_and_value = 'asdf'


class test_configfile(unittest.TestCase):

    def test_container(self):

        class TestContainer(ConfigContainer):
            a = Test1()
            b = Test2()

        ist = {}
        TestContainer()._update_schema(ist)
        soll = {'TestContainer' : {
            'Test1': {
                voluptuous.Required('type_hint_and_value', default=0): float,
                voluptuous.Required('only_type_hint'): int,
                voluptuous.Required('only_value', default=7.5): float,
            },
            'Test2' : {
                voluptuous.Required('type_hint_and_value', default='asdf'): str,
            }
        }}
        self.assertDictEqual(soll, ist)

    def test_update_default(self):

        class TestContainer(ConfigContainer):
            a = Test1()
            b = Test2()

        ist = {}
        TestContainer()._update_yaml(ist)
        soll = {'TestContainer' : {
            'Test1': {
                'type_hint_and_value': 0,
                'only_value': 7.5,
            },
            'Test2' : {
                'type_hint_and_value': 'asdf',
            }
        }}
        self.assertDictEqual(soll, ist)

        ist['TestContainer']['Test1']['type_hint_and_value'] = 99

        TestContainer()._update_yaml(ist)
        soll['TestContainer']['Test1']['type_hint_and_value'] = 99
        self.assertDictEqual(soll, ist)


if __name__ == "__main__":
    import logging
    import sys
    _log = logging.getLogger()
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(logging.Formatter("[{asctime:s}] [{name:25s}] {levelname:8s} | {message:s}", style='{'))
    _log.addHandler(ch)

    unittest.main()
