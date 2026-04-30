import sys
from parsing_config import fetch_config
from mazegen import MazeGenerator
from output_generator import generate_output_file
from maze_regenerator import maze_regenerator


def main() -> None:
    try:
        if len(sys.argv) > 2:
            raise ValueError("Too many arguments")
        elif len(sys.argv) == 1:
            raise ValueError("No arguments given")
        file = sys.argv[1]
        config = fetch_config(file)
        maze = MazeGenerator(
            config.WIDTH,
            config.HEIGHT,
            config.ENTRY,
            config.EXIT,
            config.PERFECT,
            config.SEED,
        )
        generate_output_file(maze, config.OUTPUT_FILE)
        regen = maze_regenerator(config)
        from test_mlx import setup_and_run
        setup_and_run(maze, regen)
    except FileNotFoundError:
        print(f"File {file} not found")
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()
