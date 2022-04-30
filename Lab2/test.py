import unittest

from factory import create_serializer
from test_values import example_butoma, Test, Example


class SerializerTest(unittest.TestCase):
    def test_serializer_factory(self):
        try:
            create_serializer("something useful")
        except NameError:
            pass
        else:
            assert False

    def test_json(self):
        serializer = create_serializer("json")
        with open("example_butoma.json", "r") as f:
            json_func = serializer.dumps(example_butoma)
            self.assertEqual(json_func, f.read())
        self.assertEqual(serializer.loads(json_func)(), example_butoma())
        with open("test.json", "r") as f:
            json_test = serializer.dumps(Test())
            self.assertEqual(json_test, f.read())
        self.assertEqual(serializer.loads(json_test).__dict__, Test().__dict__)

    def test_yaml(self):
        '''serializer = create_serializer("yaml")
        with open("example_butoma.yaml", "r") as f:
            json_func = serializer.dumps(example_butoma)
            self.assertEqual(json_func, f.read())
        self.assertEqual(serializer.loads(json_func)(), example_butoma())
        with open("test.yaml", "r") as f:
            json_test = serializer.dumps(Test())
            self.assertEqual(json_test, f.read())
        self.assertEqual(serializer.loads(json_test).__dict__, Test().__dict__)'''

    def test_toml(self):
        serializer = create_serializer("toml")
        with open("example_butoma.toml", "r") as f:
            json_func = serializer.dumps(example_butoma)
            self.assertEqual(json_func, f.read())
        self.assertEqual(serializer.loads(json_func)(), example_butoma())
        with open("test.toml", "r") as f:
            json_test = serializer.dumps(Example())
            self.assertEqual(json_test, f.read())
        self.assertEqual(serializer.loads(json_test).__dict__, Example().__dict__)
