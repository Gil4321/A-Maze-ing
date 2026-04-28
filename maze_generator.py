from parsing_basemodel import fetch_config
import random
import sys
from enum import Enum
sys.setrecursionlimit(99999999)


class Directions(Enum):
    NORTH = (0, -1)
    SOUTH = (0, 1)
    EAST = (1, 0)
    WEST = (-1, 0)


class WallValues(Enum):
    TOP = 1
    BOT = 4
    EAST = 2
    WEST = 8


class MazeError(Exception):
    def __init__(self, error: str) -> None:
        super().__init__(error)


class Cell:
    def __init__(self, coordinates: tuple[int, int]) -> None:
        self.coordinates = coordinates
        self.walls: int = 15
        self.visited: bool = False


class MazeGenerator:
    def __init__(
            self,
            width: int,
            height: int,
            entry: tuple[int, int],
            exit: tuple[int, int],
            perfect: bool
            ) -> None:
        self.width = width
        self.height = height
        self.entry = entry
        self.exit = exit
        self.path: list[tuple[int, int]] = []
        self.layout: list[list[Cell]] = self.initialize_layout(width, height)
        if width >= 8 and height >= 6:
            self.add_42_pattern()
        else:
            print("Could not add 42 pattern, maze is too small")
        x, y = entry
        self.create_perfect_maze(self.layout[x][y])
        if perfect is False:
            self.create_unperfect_maze()

    @staticmethod
    def initialize_layout(x: int, y: int) -> list[list[Cell]]:
        layout = []
        for i in range(x):
            vertical_row = [Cell((i, j)) for j in range(y)]
            layout.append(vertical_row)
        return layout

    def add_42_pattern(self) -> None:
        if self.width % 2 == 0:
            x = self.width // 2 - 4
        else:
            x = self.width // 2 - 3
        if self.height % 2 == 0:
            y = self.height // 2 - 3
        else:
            y = self.height // 2 - 2
        self.layout[x][y].visited = True
        self.layout[x][y + 1].visited = True
        self.layout[x][y + 2].visited = True
        self.layout[x + 1][y + 2].visited = True
        self.layout[x + 2][y + 2].visited = True
        self.layout[x + 2][y + 3].visited = True
        self.layout[x + 2][y + 4].visited = True
        self.layout[x + 4][y + 4].visited = True
        self.layout[x + 5][y + 4].visited = True
        self.layout[x + 6][y + 4].visited = True
        self.layout[x + 4][y + 3].visited = True
        self.layout[x + 4][y + 2].visited = True
        self.layout[x + 5][y + 2].visited = True
        self.layout[x + 6][y + 2].visited = True
        self.layout[x + 6][y + 1].visited = True
        self.layout[x + 6][y].visited = True
        self.layout[x + 5][y].visited = True
        self.layout[x + 4][y].visited = True
        x1, y1 = self.entry
        x2, y2 = self.exit
        if self.layout[x1][y1].visited is True:
            raise MazeError("Entry coordinates are on the 42 pattern")
        elif self.layout[x2][y2].visited is True:
            raise MazeError("Exit coordinates are on the 42 pattern ")

    def destoy_walls(self,
                     cell: Cell,
                     new_cell: Cell,
                     choice: tuple[int, int]
                     ) -> None:
        if new_cell.visited is True:
            return
        if choice == (0, -1):
            cell.walls -= 1
            new_cell.walls -= 4
        elif choice == (1, 0):
            cell.walls -= 2
            new_cell.walls -= 8
        elif choice == (0, 1):
            cell.walls -= 4
            new_cell.walls -= 1
        elif choice == (-1, 0):
            cell.walls -= 8
            new_cell.walls -= 2

    def valid_direction(
            self,
            cell: Cell,
            random_direction: tuple[int, int]
            ) -> bool:
        try:
            x1, y1 = cell.coordinates
            x2, y2 = random_direction
            if (x1 + x2) < 0 or (y1 + y2) < 0:
                return False
            new_cell: Cell = self.layout[x1 + x2][y1 + y2]
            if new_cell.visited is True:
                return False
            else:
                return True
        except IndexError:
            return False

    def path_directions(self, cell: Cell) -> list[tuple[int, int]]:
        availabe_paths = []
        directions = [
            (0, -1),
            (1, 0),
            (0, 1),
            (-1, 0)
            ]
        while directions:
            random_direction = random.choice(directions)
            directions.remove(random_direction)
            if self.valid_direction(cell, random_direction):
                availabe_paths.append(random_direction)
        return availabe_paths

    def create_perfect_maze(self, cell: Cell) -> None:
        cell.visited = True
        available_paths = self.path_directions(cell)
        for path in available_paths:
            x1, y1 = cell.coordinates
            x2, y2 = path
            new_cell = self.layout[x1 + x2][y1 + y2]
            self.destoy_walls(cell, new_cell, path)
            self.create_perfect_maze(new_cell)

    def create_unperfect_maze(self) -> None:
        x = 0
        while x < self.width:
            y = 0
            x2 = x + 3
            if x2 > self.width:
                x2 = self.width
            x_range = [i for i in range(x, x2)]
            while y < self.height:
                y2 = y + 3
                if y2 > self.height:
                    y2 = self.height
                y_range = [i for i in range(y, y2)]
                self.find_random_valid_cell(x_range, y_range)
                y = y + 3
            x = x + 3

    def find_random_valid_cell(self, x_range, y_range) -> None:
        found_valid_cell = False
        coordinates_values = []
        for x in x_range:
            for y in y_range:
                coordinates_values.append((x, y))
        while coordinates_values and found_valid_cell is False:
            coordinates = random.choice(coordinates_values)
            coordinates_values.remove(coordinates)
            try:
                x, y = coordinates
                cell: Cell = self.layout[x][y]
                if cell.walls != 15:
                    found_valid_cell = self.destroy_random_wall(cell)
            except IndexError:
                pass

    def valid_neighbor(self, cell: Cell, wall: int) -> bool:
        x, y = cell.coordinates
        try:
            if wall == 8:
                neighbor = self.layout[x - 1][y]
            elif wall == 4:
                neighbor = self.layout[x][y + 1]
            elif wall == 2:
                neighbor = self.layout[x + 1][y]
            else:
                neighbor = self.layout[x][y - 1]
            if neighbor.walls == 15:
                return False
            cell.walls -= wall
            if wall >= 4:
                neighbor.walls -= wall // 4
            else:
                neighbor.walls -= wall * 4
            return True
        except IndexError:
            return False

    def destroy_random_wall(self, cell: Cell) -> bool:
        try:
            if cell.walls == 15:
                return False
            walls = [8, 4, 2, 1]
            x, y = cell.coordinates
            if x == 0:
                walls.remove(8)
            if x == self.width - 1:
                walls.remove(2)
            if y == 0:
                walls.remove(1)
            if y == self.height - 1:
                walls.remove(4)
            while walls:
                wall = random.choice(walls)
                walls.remove(wall)
                if wall & cell.walls:
                    if self.valid_neighbor(cell, wall):
                        return True
            return False
        except IndexError:
            return False


class BFS:
    def __init__(self, maze: MazeGenerator) -> None:
        self.path_list: list[list[tuple[int, int]]] = []
        for row in maze.layout:
            for cell in row:
                cell.visited = False
        self.maze = maze

    def find_directions(self, cell: Cell) -> list[tuple[int, int]]:
        valid_coordinates = []
        x, y = cell.coordinates
        if not (8 & cell.walls) and not self.maze.layout[x - 1][y].visited:
            valid_coordinates.append(self.maze.layout[x - 1][y].coordinates)
        if not (4 & cell.walls) and not self.maze.layout[x][y + 1].visited:
            valid_coordinates.append(self.maze.layout[x][y + 1].coordinates)
        if not (2 & cell.walls) and not self.maze.layout[x + 1][y].visited:
            valid_coordinates.append(self.maze.layout[x + 1][y].coordinates)
        if not (1 & cell.walls) and not self.maze.layout[x][y - 1].visited:
            valid_coordinates.append(self.maze.layout[x][y - 1].coordinates)
        return valid_coordinates

    def initialize_entry_paths(self) -> None:
        x, y = self.maze.entry
        starting_cell = self.maze.layout[x][y]
        starting_cell.visited = True
        valid_coordinates = self.find_directions(starting_cell)
        for coordinates in valid_coordinates:
            self.path_list.append([coordinates])

    def solve_maze(self) -> list[tuple[int, int]]:
        self.initialize_entry_paths()
        while self.path_list:
            for path in self.path_list:
                if path[-1] == self.maze.exit:
                    self.maze.path = path
                x, y = path[-1]
                cell: Cell = self.maze.layout[x][y]
                cell.visited = True
                valid_coordinates = self.find_directions(cell)
                if len(valid_coordinates) >= 2:
                    for coordinates in valid_coordinates:
                        self.path_list.append(path + [coordinates])
                    self.path_list.remove(path)
                elif valid_coordinates:
                    for coordinates in valid_coordinates:
                        path.append(coordinates)
        raise MazeError("No path to exit found")


def show_maze_output(maze: MazeGenerator) -> None:
    """Test function"""
    maze.output = []
    for i in range(maze.height):
        row = [maze.layout[j][i].walls for j in range(maze.width)]
        maze.output.append(row)
        print(row)


def main() -> None:
    try:
        if len(sys.argv) > 2:
            raise ValueError("Too many arguments")
        elif len(sys.argv) == 1:
            raise ValueError("No arguments given")
        file = sys.argv[1]
        config = fetch_config(file)
        random.seed(config.SEED)
        maze = MazeGenerator(
            config.WIDTH,
            config.HEIGHT,
            config.ENTRY,
            config.EXIT,
            config.PERFECT
            )
        bfs = BFS(maze)
        bfs.solve_maze()
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()
