import unittest
from pathlib import Path

from EasyCo import ConfigEntry, ConfigContainer, ConfigFile


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

        f = Test(Path(__file__).with_name('test_files') / 'test.yml')
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
