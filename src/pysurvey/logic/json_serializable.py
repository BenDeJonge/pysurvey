# Standard library.
from pathlib import Path
from typing import Self, Union
import os

import msgspec


class JsonSerializable(msgspec.Struct):
    """
    A base class for a `JSON` (de)serializable object.

    Inherit from this class in other dataclasses to get access to quick JSON serialization.
    Here is a quick example of how to instantiate your classes:

    ```python
    # This class is an element of the main class that will be serialized.
    class MyEnum:
        Variant0 = 0
        Variant1 = 1
        Variant2 = 2

    # This is a nested dataclass that will be (recursively) serialized.
    @dataclass
    class MyClass(JsonSerializable):
        attr_int: int
        attr_str: str

    def my_method(self) -> str:
        return self.attr_str * self.attr_int

    # This is the main class that will be serialized.
    @dataclass
    class MyDataClass(JsonSerializable):
        attr_int: int
        attr_str: str
        attr_enum: MyEnum
        attr_class: MyClass
    ```

    Serialization and deserialization is then trivially achieved using:

    ```
    my_instance = MyDataClass(
        attr_int=123,
        attr_str="hello world",
        attr_enum=MyEnum.Variant0,
        attr_class=MyClass(1, "howdy", np.arange(8).reshape(2, 4)),
    )
    p = Path("my_instance.json")
    # Serializing to a dictionary or file.
    json_dict = my_instance.to_json()
    my_instance.write_json(p)
    # Deserializing from a dictionary or file.
    new_instance_from_dict = MyDataClass.from_json(json_dict)
    new_instance_from_file = MyDataClass.read_json(p)
    ```
    """

    def __repr__(self) -> str:
        """Get a `str` representation."""
        return self.to_json().decode(encoding="utf-8")

    # --------------------------------------------------------------------------
    # D E S E R I A L I Z E R S
    # --------------------------------------------------------------------------
    @classmethod
    def read_json(cls, path: Union[Path, str, bytes]) -> Self:
        """Parse a file in `JSON` format to a class instance."""
        with open(path, "rb") as f:
            return cls.from_json(f.read())

    @classmethod
    def from_json(cls, json: bytes) -> Self:
        """Parse a `dict` in `JSON` format to a class instance."""
        return msgspec.json.decode(json, type=cls)

    # --------------------------------------------------------------------------
    # S E R I A L I Z E R S
    # --------------------------------------------------------------------------
    def to_json(self, indent: int = 4) -> bytes:
        """
        Write the instance to a `dict` in `JSON` format.
        Non-initialized fields are ignored, as these cannot be deserialized.
        """
        return msgspec.json.format(buf=msgspec.json.encode(self), indent=indent)

    def write_json(
        self,
        path: Union[Path, str],
        create: bool = True,
        indent: int = 4,
    ) -> None:
        """
        Write the instance to a file in `JSON` format.

        Parameters
        ----------
        `path : Union[Path, str]`
            The path to write to, should point to a `.json` file.
        `create : bool`, optional
            Whether (`True`) or not (`False`) to automatically create the `path` directory.
            By default `True`.
        `indent : str`, optional
            The number of spaces to indent the `JSON` object. By default `4`.

        Raises
        ------
        `FileNotFoundError`
            Raised when the path is not a valid `.JSON` file.
        `FileNotFoundError`
            Raised when the parent directory cannot be created.
        """
        # Check for valid file.
        path = Path(path)
        if path.suffix.upper() != ".JSON":
            raise FileNotFoundError(
                "Expected path to be a valid .JSON file", path
            )
        # Create parent directory if needed.
        folder = os.path.dirname(path)
        if create and folder and not os.path.exists(folder):
            try:
                os.makedirs(folder, exist_ok=True)
            except FileNotFoundError:
                raise FileNotFoundError(
                    "Cannot create the parent directory", folder
                )
        # Start writing, using the name attribute for `Enum` keys.
        with open(path, "wb") as f:
            f.write(self.to_json(indent=indent))
