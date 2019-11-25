import io
import typing
import unittest
from pathlib import Path

from EasyCo import ConfigContainer, ConfigEntry, ConfigFile, EasyCoConfig

TEST_DIR = Path(__file__).with_name('test_files')


class SUB_CONTAINER(ConfigContainer):
    SUB_INT: int = 5
    SUB_FLOAT: float = 5.0
    SUB_FLOAT_COMMENT: float = 5.5
    SUB_MUTABLE_LIST: typing.List[str] = ConfigEntry()


class MyTestfile(ConfigFile):
    TOP_LEVEL_STR: str
    TOP_LEVEL_ENTRY: float = 4.4
    bla = SUB_CONTAINER()

    _cfg = EasyCoConfig()


class test_configfile(unittest.TestCase):

    def test_const(self):

        class asdf(ConfigContainer):
            my_int: int = 5
            my_float: float = 3.3
            my_float_comment: float = ConfigEntry(default=5.5, description='testest')

        class Test(ConfigFile):
            a = asdf()
            top_level_str: str = 'adsf'
            top_level_entry: float = ConfigEntry(default=5.5, description=' testest')

        f = Test(TEST_DIR / 'test.yml')
        self.assertIsInstance(f.a, asdf)
        self.assertIsInstance(f.top_level_str, str)
        self.assertIsInstance(f.top_level_entry, ConfigEntry)

        f.load()
        self.assertIsInstance(f.a, asdf)
        self.assertIsInstance(f.top_level_str, str)
        self.assertIsInstance(f.top_level_entry, float)

        f.load()
        self.assertIsInstance(f.a, asdf)
        self.assertIsInstance(f.top_level_str, str)
        self.assertIsInstance(f.top_level_entry, float)


    def test_load_lower(self):

        file = MyTestfile(TEST_DIR / 'test_lowercase.yml')
        file._cfg.lower_case_keys = True
        file.load()

        self.assertEqual(file.TOP_LEVEL_ENTRY, 9.9)
        self.assertEqual(file.TOP_LEVEL_STR, 'UPPER_lower')

        self.assertEqual(file.bla.SUB_INT, 7)
        self.assertEqual(file.bla.SUB_FLOAT, 7.0)
        self.assertEqual(file.bla.SUB_FLOAT_COMMENT, 7.7)
        self.assertListEqual(file.bla.SUB_MUTABLE_LIST, ['ListEntry'])

    def test_load_upper(self):

        file = MyTestfile(TEST_DIR / 'test_uppercase.yml')
        file._cfg.lower_case_keys = False
        file.load()

        self.assertEqual(file.TOP_LEVEL_ENTRY, 9.9)
        self.assertEqual(file.TOP_LEVEL_STR, 'UPPER_lower')

        self.assertEqual(file.bla.SUB_INT, 7)
        self.assertEqual(file.bla.SUB_FLOAT, 7.0)
        self.assertEqual(file.bla.SUB_FLOAT_COMMENT, 7.7)
        self.assertListEqual(file.bla.SUB_MUTABLE_LIST, ['ListEntry'])

    def test_string_io(self):
        class ASDF(ConfigFile):
            TOP_LEVEL_STR: str = 'asdf'
            TOP_LEVEL_ENTRY: float = 4.4
            KEY_NAME: int = ConfigEntry(default=123, key_name='NAME')

        f = io.StringIO('name: 456')
        file = ASDF()
        file.load(f)

        print(f.getvalue())


if __name__ == "__main__":
    import unittest
    import logging
    import sys

    _log = logging.getLogger()
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(logging.Formatter("[{asctime:s}] [{name:25s}] {levelname:8s} | {message:s}", style='{'))
    _log.addHandler(ch)

    unittest.main()
