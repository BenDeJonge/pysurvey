# Standard library.
import unittest
from pathlib import Path
import os
from dataclasses import field
from enum import Enum


# Local.
from pysurvey import JsonSerializable


class MyEnum(Enum):
    Variant0 = 0
    Variant1 = 1
    Variant2 = 2


class MyClass(JsonSerializable):
    attr_int: int
    attr_str: str
    attr_int_plus_one: int = field(init=False)

    def __post_init__(self):
        self.attr_int_plus_one = self.attr_int + 1


class MyDataClass(JsonSerializable):
    attr_int: int
    attr_str: str
    attr_enum: MyEnum
    attr_class: MyClass


class TestSettings(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.instance = MyDataClass(
            attr_int=123,
            attr_str="hello tests",
            attr_enum=MyEnum.Variant0,
            attr_class=MyClass(
                attr_int=456,
                attr_str="goodbye tests",
            ),
        )
        cls.path = Path("test/temp.json")

    def test_json(self):
        """Test if Settings objects can be properly serialized and deserialized."""
        inst = self.instance
        # Objects.
        self.assertEqual(inst, MyDataClass.from_json(inst.to_json()))
        # Files.
        inst.write_json(path=self.path)
        self.assertEqual(inst, MyDataClass.read_json(self.path))

    @classmethod
    def tearDownClass(cls) -> None:
        """Remove created temporary files."""
        os.remove(cls.path)
        return super().tearDownClass()


if __name__ == "__main__":
    unittest.main()
