from typing import Callable
from parsing_config import ValidConfig
from mazegen import MazeGenerator
from output_generator import generate_output_file


def maze_regenerator(config: ValidConfig) -> Callable[[], MazeGenerator]:
    """
    Create a maze regeneration function based on a configuration.

    Args:
        config: Validated configuration object.

    Returns:
        A callable that generates a new MazeGenerator instance
        and writes it to the output file each time it is called.
    """
    def regen_maze() -> MazeGenerator:
        """
        Generate a maze instance and generate an output file.
        The generated maze instance's seed is random.

        Returns:
            A newly generated MazeGenerator instance.
        """
        maze = MazeGenerator(
            config.WIDTH,
            config.HEIGHT,
            config.ENTRY,
            config.EXIT,
            config.PERFECT,
            None
        )
        generate_output_file(maze, config.OUTPUT_FILE)
        return maze
    return regen_maze
