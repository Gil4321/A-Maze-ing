from typing import Callable
from parsing_config import ValidConfig
from mazegen import MazeGenerator
from output_generator import generate_output_file


def maze_regenerator(config: ValidConfig) -> Callable[[], MazeGenerator]:
    def regen_maze() -> MazeGenerator:
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
