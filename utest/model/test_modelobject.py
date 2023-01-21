import io
import json
import os
import pathlib
import unittest
import tempfile

from robot.model.modelobject import ModelObject
from robot.utils.asserts import assert_equal, assert_raises, assert_raises_with_msg


class Example(ModelObject):

    def __init__(self, **attrs):
        self.__dict__.update(attrs)

    def to_dict(self):
        return self.__dict__


class TestRepr(unittest.TestCase):

    def test_default(self):
        assert_equal(repr(ModelObject()), 'robot.model.ModelObject()')

    def test_module_when_extending(self):
        class X(ModelObject):
            pass
        assert_equal(repr(X()), '%s.X()' % __name__)

    def test_repr_args(self):
        class X(ModelObject):
            repr_args = ('z', 'x')
            x, y, z = 1, 2, 3
        assert_equal(repr(X()), '%s.X(z=3, x=1)' % __name__)


class TestFromDictAndJson(unittest.TestCase):

    def test_init_args(self):
        class X(ModelObject):
            def __init__(self, a=1, b=2):
                self.a = a
                self.b = b
        x = X.from_dict({'a': 3})
        assert_equal(x.a, 3)
        assert_equal(x.b, 2)
        x = X.from_json('{"a": "A", "b": true}')
        assert_equal(x.a, 'A')
        assert_equal(x.b, True)

    def test_other_attributes(self):
        obj = Example.from_dict({'a': 1})
        assert_equal(obj.a, 1)
        obj = Example.from_json('{"a": null, "b": 42}')
        assert_equal(obj.a, None)
        assert_equal(obj.b, 42)

    def test_not_accepted_attribute(self):
        class X(ModelObject):
            __slots__ = ['a']
        assert_equal(X.from_dict({'a': 1}).a, 1)
        error = assert_raises(ValueError, X.from_dict, {'b': 'bad'})
        assert_equal(str(error).split(':')[0],
                     f"Creating '{__name__}.X' object from dictionary failed")

    def test_json_as_bytes(self):
        obj = Example.from_json(b'{"a": null, "b": 42}')
        assert_equal(obj.a, None)
        assert_equal(obj.b, 42)

    def test_json_as_open_file(self):
        obj = Example.from_json(io.StringIO('{"a": null, "b": 42, "c": "åäö"}'))
        assert_equal(obj.a, None)
        assert_equal(obj.b, 42)
        assert_equal(obj.c, "åäö")

    def test_json_as_path(self):
        with tempfile.NamedTemporaryFile('w', encoding='UTF-8', delete=False) as file:
            file.write('{"a": null, "b": 42, "c": "åäö"}')
        try:
            for path in file.name, pathlib.Path(file.name):
                obj = Example.from_json(path)
                assert_equal(obj.a, None)
                assert_equal(obj.b, 42)
                assert_equal(obj.c, "åäö")
        finally:
            os.remove(file.name)

    def test_invalid_json_type(self):
        error = self._get_json_load_error(None)
        assert_raises_with_msg(
            ValueError, f"Loading JSON data failed: Invalid JSON data: {error}",
            ModelObject.from_json, None
        )

    def test_invalid_json_syntax(self):
        error = self._get_json_load_error('bad')
        assert_raises_with_msg(
            ValueError, f"Loading JSON data failed: Invalid JSON data: {error}",
            ModelObject.from_json, 'bad'
        )

    def test_invalid_json_content(self):
        assert_raises_with_msg(
            ValueError, "Loading JSON data failed: Expected dictionary, got list.",
            ModelObject.from_json, '["bad"]'
        )

    def _get_json_load_error(self, value):
        try:
            json.loads(value)
        except (json.JSONDecodeError, TypeError) as err:
            return str(err)


class TestToJson(unittest.TestCase):
    data = {'a': 1, 'b': [True, False], 'c': 'nön-äscii'}
    default_config = {'ensure_ascii': False, 'indent': 0, 'separators': (',', ':')}
    custom_config = {'indent': None, 'separators': (', ', ': '), 'ensure_ascii': True}

    def test_default_config(self):
        assert_equal(Example(**self.data).to_json(),
                     json.dumps(self.data, **self.default_config))

    def test_custom_config(self):
        assert_equal(Example(**self.data).to_json(**self.custom_config),
                     json.dumps(self.data, **self.custom_config))

    def test_write_to_open_file(self):
        for config in {}, self.custom_config:
            output = io.StringIO()
            Example(**self.data).to_json(output, **config)
            expected = json.dumps(self.data, **(config or self.default_config))
            assert_equal(output.getvalue(), expected)

    def test_write_to_path(self):
        with tempfile.NamedTemporaryFile(delete=False) as file:
            pass
        try:
            for path in file.name, pathlib.Path(file.name):
                for config in {}, self.custom_config:
                    Example(**self.data).to_json(path, **config)
                    expected = json.dumps(self.data, **(config or self.default_config))
                    with open(path, encoding='UTF-8') as file:
                        assert_equal(file.read(), expected)
        finally:
            os.remove(file.name)

    def test_invalid_output(self):
        assert_raises_with_msg(TypeError,
                               "Output should be None, open file or path, got integer.",
                               Example().to_json, 42)


if __name__ == '__main__':
    unittest.main()
