import unittest

from EasyCo import ConfigContainer, EasyCoConfig

CFG_TEST = EasyCoConfig()


class TestContainer(ConfigContainer):
    TYPE_HINT_AND_VALUE: float = 0
    ONLY_TYPE_HINT: int
    ONLY_VALUE = 7.5

    # config should be found even if it is inherited or has underscores
    __cfg = CFG_TEST

    # Skipped values
    __UNDERSCORE = 8

    def function_b(self) -> bool:
        pass


class TestParentContainer(ConfigContainer):
    TEST_INT = 5
    TOP_CONTAINER = TestContainer()

    # config should be found
    __cfg = CFG_TEST


class test_container(unittest.TestCase):

    def cross_test(self, obj, obj2):
        for key in obj:
            self.assertIn(key, obj2)
        for key in obj2:
            self.assertIn(key, obj)

    def test_flat_keys(self):
        schema = {}
        CFG_TEST.lower_case_keys = False
        TestContainer()._update_schema(schema, insert=False)

        for key in schema.keys():
            self.assertIn(key, ['TYPE_HINT_AND_VALUE', 'ONLY_TYPE_HINT', 'ONLY_VALUE'])

        schema = {}
        CFG_TEST.lower_case_keys = True
        TestContainer()._update_schema(schema, insert=False)

        self.cross_test(schema, ['type_hint_and_value', 'only_type_hint', 'only_value'])


    def test_container_name(self):
        CFG_TEST.lower_case_keys = True

        schema = {}
        TestContainer()._update_schema(schema)
        self.assertIn('testcontainer', schema)

        CFG_TEST.lower_case_keys = False
        TestContainer()._update_schema(schema)
        self.assertIn('TestContainer', schema)
        self.assertIn('testcontainer', schema)

    def test_container_name_double(self):
        schema = {}
        CFG_TEST.lower_case_keys = True
        TestParentContainer()._update_schema(schema, insert=False)
        self.assertIn('test_int', schema)
        self.assertIn('testcontainer', schema)
        self.cross_test(schema['testcontainer'], ['type_hint_and_value', 'only_type_hint', 'only_value'])

        schema = {}
        CFG_TEST.lower_case_keys = False
        TestParentContainer()._update_schema(schema, insert=False)
        self.assertIn('TEST_INT', schema)
        self.assertIn('TestContainer', schema)
        self.cross_test(schema['TestContainer'], ['TYPE_HINT_AND_VALUE', 'ONLY_TYPE_HINT', 'ONLY_VALUE'])


if __name__ == "__main__":
    unittest.main()
