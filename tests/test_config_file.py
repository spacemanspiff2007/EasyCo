import unittest
from pathlib import Path

from EasyCo import ConfigEntry, ConfigContainer, ConfigFile, EasyCoConfig

TEST_DIR = Path(__file__).with_name('test_files')


class SUB_CONTAINER(ConfigContainer):
    SUB_INT: int = 5
    SUB_FLOAT: float = 5.0
    SUB_FLOAT_COMMENT:float = 5.5


class Testfile(ConfigFile):
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

        file = Testfile(TEST_DIR / 'test_lowercase.yml')
        file._cfg.lower_case_keys = True
        file.load()

        self.assertEqual(file.TOP_LEVEL_ENTRY, 9.9)
        self.assertEqual(file.TOP_LEVEL_STR, 'UPPER_lower')

        self.assertEqual(file.bla.SUB_INT, 7)
        self.assertEqual(file.bla.SUB_FLOAT, 7.0)
        self.assertEqual(file.bla.SUB_FLOAT_COMMENT, 7.7)

    def test_load_upper(self):

        file = Testfile(TEST_DIR / 'test_uppercase.yml')
        file._cfg.lower_case_keys = False
        file.load()

        self.assertEqual(file.TOP_LEVEL_ENTRY, 9.9)
        self.assertEqual(file.TOP_LEVEL_STR, 'UPPER_lower')

        self.assertEqual(file.bla.SUB_INT, 7)
        self.assertEqual(file.bla.SUB_FLOAT, 7.0)
        self.assertEqual(file.bla.SUB_FLOAT_COMMENT, 7.7)



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
