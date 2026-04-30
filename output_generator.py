from mazegen import MazeGenerator


def cardinal_path(maze: MazeGenerator) -> str:
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
