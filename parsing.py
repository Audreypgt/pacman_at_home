from sys import argv
from typing import Any, Annotated
import json
from pydantic import BaseModel, Field, field_validator, ValidationInfo
from pydantic_core import PydanticUseDefault


class ArgsError(Exception):
    """Raise an error during parsing if command line arguments are incorrect"""
    pass


# todo: check json format regarding levels with Luka (Ady reuses variables
# (like lvl width), and Jolyne as attribute levels with each level inside like
# we have now), after this add the relevant fields to Configuration class
# add way to remove comments


class Configuration(BaseModel):
    highscore_filename: str = Field(default="highscore.txt")
    # levels: dict[] = ???
    width_lvl: int = Field(ge=12, le=50, default=13)
    height_lvl: int = Field(ge=12, le=50, default=13)

    lives: int = Field(le=999, default=3)
    pacgum: int = Field(default=42)
    points_per_pacgum: int = Field(default=10)
    points_per_super_pacgum: int = Field(default=50)
    points_per_ghost: int = Field(default=200)
    seed: int = Field(default=42)
    lvl_max_time: int = Field(default=90)

    @field_validator("*", mode="before")
    @classmethod
    # using a classmethod to access attributes needed, also field_validator
    # can't be applied on instance methods
    def validation_setdefault(cls, value: Any, field: ValidationInfo) -> Any:
        """Create a dummy BaseModel class to test each field and catch errors
        in order to return a default value for the given field, this allows us
        to prevent pydantic from exiting with an error in case a field is not
        filled properly
        """
        try:
            field_info: Any = (
                cls.model_fields[str(field.field_name)].asdict())

            class TestValues(BaseModel):
                # Annotated[type, x, y] adds metadata y to x,
                """type test_fields (which is our value) as Any, give it the
                metadata (for ex ge=12, le=50) and the field attributes
                (for ex default=13), the value is therefore being tested with
                the same conditions as the fields defined in Configuration
                BaseModel, if everything is good, we return the value, else we
                return the default value we put in the Field default in our
                Configuration BaseModel
                """
                test_field: Annotated[
                    Any, *field_info["metadata"],
                    Field(**field_info["attributes"])]
            TestValues(test_field=value)

            # test = TestValues(test_field=value)
            # print("field_info")
            # print(field_info)
            # print()
            # print("test")
            # print(test)
            # print()
            # print("metadata")
            # print(field_info["metadata"])
            # print()
            # print("attributes")
            # print(field_info["attributes"])
            # print()

            return value
        except Exception:
            raise PydanticUseDefault

    @field_validator("highscore_filename", mode="before")
    @classmethod
    def validation(cls, value: Any) -> Any:
        try:
            str(value)
            if not value.endswith(".txt"):
                raise ValueError
            return value
        except ValueError:
            return "highscore.txt"


def parse() -> Configuration:
    """return dict with width, length... as key and the values given in the
    config.json file
    """

    if not len(argv) == 2:
        raise ArgsError("Wrong amount of arguments, parameters should be "
                        "python program file and configuration file\n")

    if not argv[1].endswith(('.json')):
        raise ArgsError("Configuration file must be a json file\n")

    with open(argv[1], "r") as text:
        parse_file = json.load(text)

    # return an object made of each value and key of the json file as variables
    return Configuration(**parse_file)


if __name__ == "__main__":
    config = Configuration(width_lvl=14, height_lvl=14)
    print(config)

    # example of dict unpacking:
    # config = Configuration(**{"width_lvl":"14", "height_lvl":14})

    # getting our configuration back to a json format in a txt file
    # with open("file.txt", "w") as file:
    #     print(config.model_dump_json(indent=4), file=file)
