import typing
import unittest

from EasyCo import ConfigContainer, EasyCoConfig, ConfigEntry

CFG_TEST = EasyCoConfig()


class TestContainer(ConfigContainer):
    TYPE_HINT_AND_VALUE: float = 0
    ONLY_TYPE_HINT: int
    MUTABLE_LIST: typing.List[str] = ConfigEntry(default_factory=lambda: ['test'])
#    MUTABLE_DICT: typing.Dict[str, str] = ConfigEntry(default_factory=lambda: {'a':'b'})

    __cfg = CFG_TEST


class TestParentContainer(ConfigContainer):
    TEST_INT: int = 5
    TOP_CONTAINER = TestContainer()

    # config should be found
    __cfg = CFG_TEST


class test_container(unittest.TestCase):

    def cross_test(self, obj, obj2):
        for key in obj:
            self.assertIn(key, obj2)
        for key in obj2:
            self.assertIn(key, obj)

    def test_schema_flat_keys(self):
        schema = {}
        CFG_TEST.lower_case_keys = False
        TestContainer()._update_schema(schema, insert_values=False)

        for key in schema.keys():
            self.assertIn(key, ['TYPE_HINT_AND_VALUE', 'ONLY_TYPE_HINT', 'MUTABLE_LIST'])

        schema = {}
        CFG_TEST.lower_case_keys = True
        TestContainer()._update_schema(schema, insert_values=False)

        self.cross_test(schema, ['type_hint_and_value', 'only_type_hint', 'mutable_list'])


    def test_schema_container_name(self):
        CFG_TEST.lower_case_keys = True

        schema = {}
        TestContainer()._update_schema(schema)
        self.assertIn('testcontainer', schema)

        CFG_TEST.lower_case_keys = False
        TestContainer()._update_schema(schema)
        self.assertIn('TestContainer', schema)
        self.assertIn('testcontainer', schema)

    def test_schema_container_name_double(self):
        schema = {}
        CFG_TEST.lower_case_keys = True
        TestParentContainer()._update_schema(schema, insert_values=False)
        self.assertIn('test_int', schema)
        self.assertIn('testcontainer', schema)
        self.cross_test(schema['testcontainer'], ['type_hint_and_value', 'only_type_hint', 'mutable_list'])

        schema = {}
        CFG_TEST.lower_case_keys = False
        TestParentContainer()._update_schema(schema, insert_values=False)
        self.assertIn('TEST_INT', schema)
        self.assertIn('TestContainer', schema)
        self.cross_test(schema['TestContainer'], ['TYPE_HINT_AND_VALUE', 'ONLY_TYPE_HINT', 'MUTABLE_LIST'])

    def test_value_container(self):
        CFG_TEST.lower_case_keys = False

        data = {
            'TYPE_HINT_AND_VALUE': 9.0,
            'ONLY_TYPE_HINT': 7,
            'ADDITIONAL_KEY': 7.5,
        }

        obj = TestContainer()
        self.assertEqual(obj.TYPE_HINT_AND_VALUE, 0)
        obj._set_value(data)
        self.assertEqual(obj.TYPE_HINT_AND_VALUE, 9.0)
        self.assertEqual(obj.ONLY_TYPE_HINT, 7)

    def test_value_parent_container(self):
        CFG_TEST.lower_case_keys = False

        data = {
            'TEST_INT': 7,
            'TestContainer': {
                'TYPE_HINT_AND_VALUE': 9.0,
                'ONLY_TYPE_HINT': 7,
                'ADDITIONAL_KEY': 7.5,
            }
        }

        obj = TestParentContainer()
        obj._set_value(data)
        self.assertEqual(obj.TEST_INT, 7)

        self.assertEqual(obj.TOP_CONTAINER.TYPE_HINT_AND_VALUE, 9.0)
        self.assertEqual(obj.TOP_CONTAINER.ONLY_TYPE_HINT, 7)


    def test_subscribe(self):
        CFG_TEST.lower_case_keys = False

        self.called = 0

        def func1():
            self.called += 1

        def func2():
            self.called += 1

        data = {
            'TYPE_HINT_AND_VALUE': 9.0,
            'ONLY_TYPE_HINT': 7,
            'ADDITIONAL_KEY': 7.5,
        }
        obj = TestContainer()
        obj.subscribe_for_changes(func1)
        obj.subscribe_for_changes(func2)

        self.assertEqual(self.called, 0)
        self.assertEqual(obj.TYPE_HINT_AND_VALUE, 0)
        obj._set_value(data)
        self.assertEqual(obj.TYPE_HINT_AND_VALUE, 9.0)
        self.assertEqual(self.called, 2)



if __name__ == "__main__":
    unittest.main()
