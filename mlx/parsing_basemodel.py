from pydantic import BaseModel, field_validator, model_validator
import random


class ParsingError(Exception):
    def __init__(self, error: str):
        super().__init__(error)


class ValidConfig(BaseModel):
    WIDTH: int
    HEIGHT: int
    ENTRY: tuple[int, int]
    EXIT: tuple[int, int]
    OUTPUT_FILE: str
    PERFECT: bool
    SEED: float
    CONFIG_FILE: str

    @field_validator("WIDTH", "HEIGHT", mode="before")
    @classmethod
    def validate_dimensions(cls, size: str) -> int:
        try:
            parsed_size = int(size)
        except Exception:
            raise ParsingError(
                f"Value {size} is not an int. Values can only be integers "
                "and > 0 for WIDTH and HEIGHT"
                )
        if parsed_size < 1:
            raise ParsingError(
                f"Value {size} cannot be < 1 for WIDTH and HEIGHT"
                )
        return parsed_size

    @field_validator("ENTRY", "EXIT", mode="before")
    @classmethod
    def format_coordinates(cls, coordinates: str) -> tuple[str, str]:
        split_coordinates = coordinates.split(",")
        if len(split_coordinates) != 2:
            raise ParsingError(
                f"Wrong format for value: {coordinates}. Try "
                "'value(int),value(int)' for ENTRY and EXIT"
                )
        try:
            for value in split_coordinates:
                _ = int(value)
        except Exception:
            raise ParsingError(
                f"Value: {value} in {split_coordinates} is not an int. "
                "Values can only be positive integers for ENTRY and EXIT"
                )
        return (split_coordinates[0], split_coordinates[1])

    @field_validator("PERFECT", mode="before")
    @classmethod
    def validate_maze_type(cls, maze_type: str) -> bool:
        if maze_type == "True" or maze_type == "":
            return True
        elif maze_type == "False":
            return False
        raise ParsingError(
            f"Value '{type}' invalid. Maze type must be True, "
            "False or left empty for key 'PERFECT'"
            )

    @field_validator("SEED", mode="before")
    @classmethod
    def validate_seed(cls, seed: str) -> float:
        if seed == "":
            return float(random.randrange(999999))
        try:
            parsed_seed = float(seed)
        except Exception:
            raise ParsingError("SEED must be and int, a float or left empty")
        if parsed_seed < 0:
            parsed_seed = parsed_seed * -1
        return parsed_seed

    @model_validator(mode="after")
    def validate_file_name(self) -> BaseModel:
        if not self.OUTPUT_FILE.endswith('.txt'):
            raise ParsingError("Output file must end with '.txt'")
        elif self.OUTPUT_FILE == self.CONFIG_FILE:
            raise ParsingError(
                "Output file cannot have the same name as config file"
                )
        if self.ENTRY == self.EXIT:
            raise ParsingError(
                "'ENTRY' and 'EXIT' cannot have the same coordinates"
                )
        x, y = self.ENTRY
        if x + 1 > self.WIDTH:
            raise ParsingError("Coordinate 'x' of key 'ENTRY' is out of range")
        elif y + 1 > self.HEIGHT:
            raise ParsingError("Coordinate 'y' of key 'ENTRY' is out of range")
        x, y = self.EXIT
        if x + 1 > self.WIDTH:
            raise ParsingError("Coordinate 'x' of key 'EXIT' is out of range")
        elif y + 1 > self.HEIGHT:
            raise ParsingError("Coordinate 'y' of key 'EXIT' is out of range")
        return self


def fetch_config(file_name: str) -> ValidConfig:
    try:
        keys = [
            "WIDTH",
            "HEIGHT",
            "ENTRY",
            "EXIT",
            "OUTPUT_FILE",
            "PERFECT",
            "SEED"
            ]
        config: dict = {}
        with open(file_name, "r") as file:
            content = file.readline()
            while content:
                if content.startswith(('#', '\n')):
                    pass
                else:
                    split_content = content.split("=")
                    if len(split_content) != 2:
                        raise ParsingError(
                            f"Wrong format for '{content}'. try 'KEY=value'"
                            )
                    key, value = split_content
                    if key not in keys:
                        raise ParsingError(
                            f"Key '{key}' not valid. "
                            f"List of valid keys: {keys}"
                            )
                    elif key in keys and key in config.keys():
                        raise ParsingError(f"Key '{key}' found twice")
                    config[key] = value.rstrip()
                content = file.readline()
            if len(keys) != len(config.keys()):
                missing = []
                for key in keys:
                    if key not in config.keys():
                        missing.append(key)
                raise ParsingError(f"Keys: {missing} missing from config file")
            config = ValidConfig(
                WIDTH=config['WIDTH'],
                HEIGHT=config['HEIGHT'],
                ENTRY=config['ENTRY'],
                EXIT=config['EXIT'],
                OUTPUT_FILE=config['OUTPUT_FILE'],
                PERFECT=config['PERFECT'],
                SEED=config['SEED'],
                CONFIG_FILE=file_name
                )
        return config
    except Exception as e:
        raise (e)


if __name__ == "__main__":
    try:
        config = fetch_config("config.txt")
        config = config.model_dump()
        print(config)
    except Exception as e:
        print(e)
