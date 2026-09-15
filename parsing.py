from sys import argv
from typing import Any, Annotated
import json
from collections.abc import Callable
from pydantic import (
    BaseModel, Field, field_validator, ValidationInfo)
from pydantic_core import PydanticUseDefault


class ArgsError(Exception):
    """Raise an error during parsing if command line arguments
        are incorrect."""
    pass


class LevelConfiguration(BaseModel):
    """Use BaseModel to implement a default value in case of incorrect value
    for level specific attributes.
    """
    seed: int = Field(default=0)
    pacgum: int = Field(default=207)


class Configuration(BaseModel):
    """Use BaseModel to implement a default value if value is incorrect."""
    highscore_filename: str = Field(default="highscore.txt")
    levels: dict[str, LevelConfiguration] = Field(default={
        "level_1": LevelConfiguration(),
        "level_2": LevelConfiguration(
            seed=0,
            pacgum=207
        ),
        "level_3": LevelConfiguration(
            seed=0,
            pacgum=207
        ),
        "level_4": LevelConfiguration(
            seed=0,
            pacgum=207
        ),
        "level_5": LevelConfiguration(
            seed=0,
            pacgum=207
        ),
        "level_6": LevelConfiguration(
            seed=0,
            pacgum=207
        ),
        "level_7": LevelConfiguration(
            seed=0,
            pacgum=207
        ),
        "level_8": LevelConfiguration(
            seed=0,
            pacgum=207
        ),
        "level_9": LevelConfiguration(
            seed=0,
            pacgum=207
        ),
        "level_10": LevelConfiguration(
            seed=0,
            pacgum=207
        )})
    lives: int = Field(le=999, default=3)
    points_per_pacgum: int = Field(ge=0, default=10)
    points_per_super_pacgum: int = Field(ge=0, default=50)
    points_per_ghost: int = Field(ge=0, default=200)
    lvl_max_time: int = Field(ge=0, default=120)

    @field_validator("*", mode="before")
    @classmethod
    # using a classmethod to access attributes needed, also field_validator
    # can't be applied on instance methods
    def validation_setdefault(cls, value: Any, field: ValidationInfo) -> Any:
        """Create a dummy BaseModel class to test each field and catch errors
        in order to return a default value for the given field, this allows us
        to prevent pydantic from exiting with an error in case a field is not
        filled properly.
        """
        try:
            field_info: Any = (
                cls.model_fields[str(field.field_name)].asdict())

            class TestValues(BaseModel):
                """Type test_fields (which is our value) as Any, give it the
                metadata (for ex ge=12, le=50) and the field attributes
                (for ex default=13), the value is therefore being tested with
                the same conditions as the fields defined in Configuration
                BaseModel, if everything is good, we return the value, else we
                return the default value we put in the Field default in our
                Configuration BaseModel.
                """
                # Annotated[type, x, y] adds metadata y to x,
                test_field: Annotated[
                    Any, *field_info["metadata"],
                    Field(**field_info["attributes"])]
            TestValues(test_field=value)
            return value
        except Exception:
            field_info = cls.model_fields[str(field.field_name)]
            print("Config file warning:")
            print(f"{field.field_name} value '{value}' is invalid.")
            print(f"Using default value: {field_info.get_default()}")
            raise PydanticUseDefault

    @field_validator("levels", mode="before")
    @classmethod
    def validation_level(cls, value: Any) -> Any:
        """create a dictionary containing each level and validating them
        using LevelConfiguration class.
        """
        index: int = 1
        levels: dict[str, LevelConfiguration] = {}
        try:
            for index, level in enumerate(value.values(), start=1):
                levels["level_" + str(index)] = LevelConfiguration(**level)
            return levels
        except Exception:
            raise PydanticUseDefault

    @field_validator("highscore_filename", mode="before")
    @classmethod
    def validation(cls, value: Any) -> Any:
        """validate field highscore_filename, must be a string with .txt
        extension.
        """
        try:
            str(value)
            if not value.endswith(".txt"):
                raise ValueError
            return value
        except ValueError:
            print("Score file should end with '.txt', value will be set to "
                  "default.")
            return "highscore.txt"


class JSONWithCommentsDecoder(json.JSONDecoder):
    """Ignore comments in json configuration file."""
    def __init__(self, **kw: Any) -> None:
        """"Initialize class that inherits from JSONDecoder."""
        super().__init__(**kw)

    def decode(self, s: str, _: Callable[..., Any] = lambda: "") -> Any:
        """Create a string with the configuration, removing the lines
        starting with # or //."""
        s = '\n'.join(
            line if not line.lstrip().startswith(('//', '#'))
            else '' for line in s.split('\n'))
        return super().decode(s)


def parse() -> Configuration:
    """Check that given command line arguments are correct and return
    dict with varibale names as keys and the values given in the
    configuration file in order to use it in our program.
    """
    if not len(argv) == 2:
        raise ArgsError("Wrong amount of arguments, parameters should be "
                        "excactly: python file - configuration file\n")

    if not argv[1].endswith((".json")):
        raise ArgsError("Configuration file must be a json file\n")

    with open(argv[1], "r") as file:
        parse_file = json.load(file, cls=JSONWithCommentsDecoder)

    try:
        level_list = [
            "level_1", "level_2", "level_3", "level_4",
            "level_5", "level_6", "level_7", "level_8", "level_9", "level_10"]

        level_key_list = ["pacgum"]

        for key in Configuration.model_fields.keys():
            if key not in parse_file.keys():
                raise KeyError(f"Missing key '{key}', value will be set to "
                               "default.")

        if not isinstance(parse_file["levels"], dict):
            raise ValueError("Key 'levels' should be a dictionary.")
        for level in level_list:
            if level not in parse_file["levels"].keys():
                raise KeyError(f"Missing level '{level}', value will be set to"
                      " default.")

        for i in range(1, 11):
            if not isinstance(parse_file["levels"][f"level_{i}"], dict):
                raise ValueError(f"Key 'level_{i}' should be a dictionary.")
            for level_key in level_key_list:
                if level_key not in parse_file["levels"][f"level_{i}"].keys():
                    raise KeyError(f"Missing level key '{level_key}', value "
                                   "will be set to default.")
    except (KeyError, ValueError) as e:
        print(e)

    return Configuration(**parse_file)


# example of dict unpacking:
# config = Configuration(**{"width_lvl":"14", "height_lvl":14})

# getting our configuration back to a json format in a txt file
# with open("file.txt", "w") as file:
#     print(config.model_dump_json(indent=4), file=file)
