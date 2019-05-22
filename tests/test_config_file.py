import unittest
from pathlib import Path

from EasyCo import ConfigEntry, ConfigContainer, ConfigFile, EasyCoConfig

TEST_DIR = Path(__file__).with_name('test_files')


class TOP_LEVEL_CONTAINER(ConfigContainer):
    SUB_INT = 7
    SUB_FLOAT: float = 7
    SUB_FLOAT_COMMENT = 7.7


class Testfile(ConfigFile):
    TOP_LEVEL_STR: str
    TOP_LEVEL_ENTRY = 0.0
    bla = TOP_LEVEL_CONTAINER()

    _cfg = EasyCoConfig()


class test_configfile(unittest.TestCase):

    def test_const(self):

        class asdf(ConfigContainer):
            my_int = 5
            my_float = 3.3
            my_float_comment = ConfigEntry(default_value=5.5, description='testest')

        class Test(ConfigFile):
            a = asdf()
            top_level_str = 'adsf'
            top_level_entry = ConfigEntry(default_value=5.5, description=' testest')

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

        self.assertEqual(file.TOP_LEVEL_ENTRY, 5.5)
        self.assertEqual(file.TOP_LEVEL_STR, 'UPPER_lower')

        self.assertEqual(file.bla.SUB_INT, 5)
        self.assertEqual(file.bla.SUB_FLOAT, 3.3)
        self.assertEqual(file.bla.SUB_FLOAT_COMMENT, 5.5)

    def test_load_upper(self):

        file = Testfile(TEST_DIR / 'test_uppercase.yml')
        file._cfg.lower_case_keys = False
        file.load()

        self.assertEqual(file.TOP_LEVEL_ENTRY, 5.5)
        self.assertEqual(file.TOP_LEVEL_STR, 'UPPER_lower')

        self.assertEqual(file.bla.SUB_INT, 5)
        self.assertEqual(file.bla.SUB_FLOAT, 3.3)
        self.assertEqual(file.bla.SUB_FLOAT_COMMENT, 5.5)



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
