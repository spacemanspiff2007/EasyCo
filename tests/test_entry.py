import io
import ruamel.yaml
import unittest

import voluptuous

from EasyCo import ConfigEntry, EasyCoConfig

CFG = EasyCoConfig()


class test_ConfigEntry(unittest.TestCase):

    def test_required(self):
        c = ConfigEntry(required=True, value_type=int)
        validator = c.set_validator('test', {})
        with self.assertRaises(voluptuous.MultipleInvalid):
            voluptuous.Schema(validator)({})
        voluptuous.Schema(validator)({'test': 5})

        c = ConfigEntry(required=False, value_type=str)
        validator = c.set_validator('test', {})
        voluptuous.Schema(validator)({})
        voluptuous.Schema(validator)({'test': 'my_str'})

    def test_default_value_create(self):
        CFG.create_optional_keys = True

        ret = {}
        ConfigEntry(required=False, default_factory=5).set_default('test_int', ret, CFG)
        self.assertDictEqual(ret, {'test_int': 5})

        ConfigEntry(required=False, default_factory='TestString').set_default('test_str', ret, CFG)
        self.assertDictEqual(ret, {'test_int': 5, 'test_str': 'TestString'})

    def test_default_value_skip(self):
        CFG.create_optional_keys = False

        ret = {}
        ConfigEntry(required=False, default_factory='skip').set_default('key_skip', ret, CFG)
        ConfigEntry(required=True, default_factory='set').set_default('key_set', ret, CFG)
        self.assertDictEqual(ret, {'key_set' : 'set'})


    def test_default_validator(self):
        c = ConfigEntry(required=True, default_factory=5)
        validator = c.set_validator('test', {})

        ret = voluptuous.Schema(validator)({})
        self.assertDictEqual(ret, {'test': 5})

        ret = voluptuous.Schema(validator)({'test': 7})
        self.assertDictEqual(ret, {'test': 7})


        c = ConfigEntry(required=True, default_factory='asdf')
        validator = c.set_validator('test', {})

        ret = voluptuous.Schema(validator)({})
        self.assertDictEqual(ret, {'test': 'asdf'})

        ret = voluptuous.Schema(validator)({'test': 'ASDF'})
        self.assertDictEqual(ret, {'test': 'ASDF'})

    def test_description(self):
        data = ruamel.yaml.comments.CommentedMap()
        ConfigEntry(required=True, default_factory=5).set_default('key_no_comment', data, CFG)
        ConfigEntry(required=True, default_factory=5, description='Description').set_default('key_comment', data, CFG)

        tmp = io.StringIO()
        ruamel.yaml.YAML().dump(data, tmp)
        output = tmp.getvalue()

        self.assertEqual('key_no_comment: 5\nkey_comment: 5  # Description\n', output)


if __name__ == "__main__":
    unittest.main()
