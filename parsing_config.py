from pydantic import BaseModel, field_validator, model_validator
from pydantic import ValidationInfo
from typing import Any


class ParsingError(Exception):
    """Custom exception raised when configuration parsing fails."""

    def __init__(self, error: str):
        super().__init__(error)


class ValidConfig(BaseModel):
    """Validated configuration model for maze generation."""
    WIDTH: int
    HEIGHT: int
    ENTRY: tuple[int, int]
    EXIT: tuple[int, int]
    OUTPUT_FILE: str
    PERFECT: bool
    SEED: str | None
    CONFIG_FILE: str

    @field_validator("WIDTH", "HEIGHT", mode="before")
    @classmethod
    def validate_dimensions(cls, size: str, info: ValidationInfo) -> int:
        """
        Validate WIDTH and HEIGHT values.

        Args:
            size: String representation of a dimension (width or height).

        Returns:
            Parsed integer value of the dimension.

        Raises:
            ParsingError: - If the value is not a valid integer.
                          - If WIDTH is > 240.
                          - If HEIGHT is > 130.
            WIDTH and HEIGHT restrictions are here to limit the size
            of the maze on a 3840 x 2160 display format because the
            mlx display cannot handle it.
        """
        try:
            parsed_size = int(size)
        except Exception:
            raise ParsingError(
                "Error: WIDTH and HEIGHT values can only be integers"
                " > 0."
            )
        if parsed_size < 1:
            raise ParsingError(
                "Error: WIDTH and HEIGHT values cannot be < 1."
            )
        if info.field_name == "WIDTH":
            if parsed_size > 240:
                raise ParsingError("Error: WIDTH value must be <= 240.")
        elif info.field_name == "HEIGHT":
            if parsed_size > 130:
                raise ParsingError("Error: HEIGHT must be <= 130.")
        return parsed_size

    @field_validator("ENTRY", "EXIT", mode="before")
    @classmethod
    def validate_coordinates(cls, coordinates: str) -> tuple[int, int]:
        """
        Validate ENTRY and EXIT coordinates.

        Args:
            coordinates: Coordinates as a string formatted "x,y".

        Returns:
            Tuple of integers (x, y).

        Raises:
            ParsingError: If the format or values are invalid.
        """
        split_coordinates = coordinates.split(",")
        if len(split_coordinates) != 2:
            raise ParsingError(
                f"Error: Wrong format for coordinates: {coordinates}. Try "
                "'value(int),value(int)' for ENTRY and EXIT."
            )
        try:
            for value in split_coordinates:
                _ = int(value)
        except Exception:
            raise ParsingError(
                "ENTRY and EXIT values can only be positive integers."
            )
        return (int(split_coordinates[0]), int(split_coordinates[1]))

    @field_validator("PERFECT", mode="before")
    @classmethod
    def validate_maze_type(cls, maze_type: str) -> bool:
        """
        Validate PERFECT flag.

        Args:
            maze_type: String value representing a boolean.

        Returns:
            Boolean value.

        Raises:
            ParsingError: If the value is invalid.
        """
        if maze_type == "True" or maze_type == "":
            return True
        elif maze_type == "False":
            return False
        raise ParsingError(
            f"Value '{maze_type}' invalid for key PERFECT. PERFECT must be"
            "True, False or left empty."
        )

    @field_validator("SEED", mode="before")
    @classmethod
    def validate_seed(cls, seed: str) -> str | None:
        """
        Validate SEED value.

        Args:
            seed: Seed value as a string.

        Returns:
            Seed string or None if empty.
        """
        if seed == "":
            return None
        return seed

    @model_validator(mode="after")
    def validate_model(self) -> 'ValidConfig':
        """
        Validate consistency of the full configuration.

        Returns:
            The validated configuration instance.

        Raises:
            ParsingError: If any consistency rule is violated.
        """
        if not self.OUTPUT_FILE.endswith('.txt'):
            raise ParsingError("Output file must end with '.txt'")
        elif self.OUTPUT_FILE == self.CONFIG_FILE:
            raise ParsingError(
                "Output file cannot have the same name as config file."
            )
        elif self.OUTPUT_FILE == 'requirements.txt':
            raise ParsingError(
                "Output file cannot have the same name as requirements file."
            )
        if self.ENTRY == self.EXIT:
            raise ParsingError(
                "'ENTRY' and 'EXIT' cannot have the same coordinates."
            )
        x, y = self.ENTRY
        if x + 1 > self.WIDTH or x < 0:
            raise ParsingError(
                "Coordinate 'x' of key 'ENTRY' is out of range. "
                "x must be < WIDTH and >= 0."
            )
        elif y + 1 > self.HEIGHT or y < 0:
            raise ParsingError(
                "Coordinate 'y' of key 'ENTRY' is out of range. "
                "y must be < HEIGHT and >= 0.")
        x, y = self.EXIT
        if x + 1 > self.WIDTH or x < 0:
            raise ParsingError(
                "Coordinate 'x' of key 'EXIT' is out of range. "
                "x must be < WIDTH and >= 0."
            )
        elif y + 1 > self.HEIGHT or y < 0:
            raise ParsingError(
                "Coordinate 'y' of key 'EXIT' is out of range. "
                "y must be < HEIGHT and >= 0.")
        return self


def fetch_config(file_name: str) -> ValidConfig:
    """
    Parse and validate a configuration file.

    Args:
        file_name: Path to the configuration file.

    Returns:
        A validated configuration object.

    Raises:
        ParsingError: If the file content is invalid or incomplete.
        OSError: If the file cannot be opened.
    """
    keys = [
        "WIDTH",
        "HEIGHT",
        "ENTRY",
        "EXIT",
        "OUTPUT_FILE",
        "PERFECT",
        "SEED"
    ]
    config: dict[str, Any] = {}
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
                        f"Key: '{key}' not valid.\n"
                        f"List of valid keys: {keys}"
                    )
                elif key in keys and key in config.keys():
                    raise ParsingError(
                        f"Key: '{key}' found twice, "
                        "cannot have duplicate keys"
                    )
                config[key] = value.rstrip()
            content = file.readline()
        if len(keys) != len(config.keys()):
            missing = []
            for key in keys:
                if key not in config.keys():
                    missing.append(key)
            raise ParsingError(f"Keys: {missing} missing from config file")
        valid_model = ValidConfig(
            WIDTH=config['WIDTH'],
            HEIGHT=config['HEIGHT'],
            ENTRY=config['ENTRY'],
            EXIT=config['EXIT'],
            OUTPUT_FILE=config['OUTPUT_FILE'],
            PERFECT=config['PERFECT'],
            SEED=config['SEED'],
            CONFIG_FILE=file_name
        )
    return valid_model
