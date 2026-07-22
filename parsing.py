from sys import argv
from typing import Any


def parse() -> dict[str, Any]:
    """return dict with width, length... as key and the values given in the
    config.json file"""
    parsed_dict: dict[str, Any] = {}
    config_keys: tuple[str, ...] = (
        "highscore_filename", "width_lvl0", "height_lvl0", "width_lvl1",
        "height_lvl1", "width_lvl2", "height_lvl2", "width_lvl3",
        "height_lvl3", "lives", "pacgum", "points_per_pacgum",
        "points_per_super_pacgum", "points_per_ghost", "seed", "lvl_max_time")

    if not len(argv) == 2:
        raise ArgsError("Wrong amount of arguments, parameters should be "
                        "python program file and configuration file\n")

    if not argv[1].endswith(('.txt', '.cfg', '.config')):
        raise ArgsError("Configuration file must be a text-based file, allowed"
                        " extension formats are .txt, .cfg and .config\n")

    with open(argv[1], "r") as text:
        parse_file = text.read().split("\n")

    # populate dict with keys and values, and check if keys are valid
    for line in parse_file:
        if line.startswith("#"):
            continue
        elif line == "":
            continue
    return parsed_dict
