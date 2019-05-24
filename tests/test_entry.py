import io, typing
import ruamel.yaml
import unittest

import voluptuous

from EasyCo import ConfigEntry, EasyCoConfig, DEFAULT_CONFIGURATION

CFG_LOWER = EasyCoConfig()
CFG_LOWER.lower_case_keys = True


class test_ConfigEntry(unittest.TestCase):

    def test_required(self):
        c = ConfigEntry(required=True, key_name='test')
        c.set_type_hint('test', int)
        validator = c.set_validator({}, CFG_LOWER)
        with self.assertRaises(voluptuous.MultipleInvalid):
            voluptuous.Schema(validator)({})
        voluptuous.Schema(validator)({'test': 5})

        c = ConfigEntry(required=False, key_name='test')
        c.set_type_hint('test', str)
        validator = c.set_validator({}, CFG_LOWER)
        voluptuous.Schema(validator)({})
        voluptuous.Schema(validator)({'test': 'my_str'})

    def test_default_value_create(self):
        CFG_LOWER.create_optional_keys = True

        ret = {}
        ConfigEntry(required=False, default=5, key_name='test_int').set_default(ret, CFG_LOWER)
        self.assertDictEqual(ret, {'test_int': 5})

        ConfigEntry(required=False, default='TestString', key_name='test_str').set_default(ret, CFG_LOWER)
        self.assertDictEqual(ret, {'test_int': 5, 'test_str': 'TestString'})

    def test_default_value_skip(self):
        CFG_LOWER.create_optional_keys = False

        ret = {}
        ConfigEntry(required=False, default='skip', key_name='key_skip').set_default(ret, CFG_LOWER)
        ConfigEntry(required=True, default='set', key_name='key_set').set_default(ret, CFG_LOWER)
        self.assertDictEqual(ret, {'key_set' : 'set'})


    def test_default_validator(self):
        c = ConfigEntry(required=True, default=5)
        c.set_type_hint('test', int)
        validator = c.set_validator({}, DEFAULT_CONFIGURATION)

        ret = voluptuous.Schema(validator)({})
        self.assertDictEqual(ret, {'test': 5})

        ret = voluptuous.Schema(validator)({'test': 7})
        self.assertDictEqual(ret, {'test': 7})


        c = ConfigEntry(required=True, default='asdf')
        c.set_type_hint('test', str)
        validator = c.set_validator({}, DEFAULT_CONFIGURATION)

        ret = voluptuous.Schema(validator)({})
        self.assertDictEqual(ret, {'test': 'asdf'})

        ret = voluptuous.Schema(validator)({'test': 'ASDF'})
        self.assertDictEqual(ret, {'test': 'ASDF'})

    def test_description(self):
        data = ruamel.yaml.comments.CommentedMap()
        ConfigEntry(required=True, default=5, key_name='key_no_comment').set_default(data, CFG_LOWER)
        ConfigEntry(required=True, default=5, key_name='key_comment',
                    description='Description').set_default(data, CFG_LOWER)

        tmp = io.StringIO()
        ruamel.yaml.YAML().dump(data, tmp)
        output = tmp.getvalue()

        self.assertEqual('key_no_comment: 5\nkey_comment: 5  # Description\n', output)

    def test_list_validator(self):

        c = ConfigEntry(required=True, default_factory=lambda: ['test'])
        c.set_type_hint('test', typing.List[str])
        validator = c.set_validator({}, DEFAULT_CONFIGURATION)

        ret = voluptuous.Schema(validator)({})
        self.assertDictEqual(ret, {'test': ['test']})

    def test_dict_validator(self):

        c = ConfigEntry(required=True, default_factory=lambda: {'test_key': 'test_val'})
        c.set_type_hint('test', typing.Dict[str, str])
        validator = c.set_validator({}, DEFAULT_CONFIGURATION)

        ret = voluptuous.Schema(validator)({})
        self.assertDictEqual(ret, {'test': {'test_key': 'test_val'}})


if __name__ == "__main__":
    unittest.main()
