from mazegen import MazeGenerator


def cardinal_path(maze: MazeGenerator) -> str:
    """
    Generate a cardinal direction path from entry to exit.

    Args:
        maze: MazeGenerator instance containing the computed path.

    Returns:
        A string representing the path using cardinal directions:
        'N', 'S', 'E', 'W', ending with a newline.
    """
    path = ""
    all_coordinates = ([maze.entry] + maze.path + [maze.exit])
    for i in range(len(all_coordinates) - 1):
        x1, y1 = all_coordinates[i]
        x2, y2 = all_coordinates[i + 1]
        if x1 > x2:
            path += 'W'
        elif x1 < x2:
            path += 'E'
        elif y1 > y2:
            path += 'N'
        elif y1 < y2:
            path += 'S'
    return (path + '\n')


def generate_output_file(
        maze: MazeGenerator,
        output: str,
) -> None:
    """
    Generate a text file representation of the maze.

    Args:
        maze: MazeGenerator instance containing maze data.
        output: Path to the output file.

    """
    path = cardinal_path(maze)
    with open(output, "w") as file:
        for y in range(maze.height):
            row = [format(
                maze.layout[x][y].walls, 'X') for x in range(maze.width)]
            for walls in row:
                file.write(walls)
            file.write('\n')
        file.write('\n' + str(maze.entry[0]) + ',' + str(maze.entry[1]))
        file.write('\n' + str(maze.exit[0]) + ',' + str(maze.exit[1]))
        file.write('\n' + path)
