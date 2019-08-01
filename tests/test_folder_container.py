import unittest
from pathlib import Path

import EasyCo
from EasyCo import PathContainer, ConfigFile

TEST_DIR = Path(__file__).with_name('test_files')


class Folder_Container(PathContainer):
    FolderA: str = 'TestA'
    FolderB: Path = 'TestB'


class MyTestFile(ConfigFile):
    folders = Folder_Container()


class test_container(unittest.TestCase):

    def test_folder(self):
        EasyCo.DEFAULT_CONFIGURATION.lower_case_keys = True

        f = Folder_Container()
        f.parent_folder = TEST_DIR
        cfg = {'foldera': 'TestFolderA', 'folderb': 'TestFolderA'}
        f._set_value(cfg)
        self.assertIsInstance(f.FolderA, Path)
        self.assertIsInstance(f.FolderB, Path)


    def test_file(self):
        EasyCo.DEFAULT_CONFIGURATION.lower_case_keys = True

        f = MyTestFile(TEST_DIR / 'test_folder')
        assert f.folders.parent_folder == TEST_DIR
        f.load()

        self.assertIsInstance(f.folders.FolderA, Path)
        self.assertIsInstance(f.folders.FolderB, Path)

        self.assertEqual(TEST_DIR / 'FolderA', f.folders.FolderA)
        self.assertEqual(TEST_DIR / 'FolderB', f.folders.FolderB)


if __name__ == "__main__":
    unittest.main()
