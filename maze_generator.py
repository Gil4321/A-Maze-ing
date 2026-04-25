from parsing_basemodel import fetch_config
import random


class Cell:
    def __init__(self, coordinates: tuple[int, int]) -> None:
        self.coordinates = coordinates
        self.walls: int = 15
        self.visited: bool = False


class Maze:
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
        self.perfect = perfect
        self.path: list[Cell] = []
        self.path_cardinal: list[str] = []
        self.path_found = False
        self.layout: list[list[Cell]] = self.initialize_layout(width, height)
        x, y = entry
        self.pos: Cell = self.layout[x][y]
        self.pos.visited = True
        self.total_cells = width * height
        self.visited_cells = 1

    @staticmethod
    def initialize_layout(x: int, y: int) -> list[list[tuple[int, int]]]:
        layout = []
        for i in range(x):
            vertical_row = [Cell((i, j)) for j in range(y)]
            layout.append(vertical_row)
        return layout

    def destoy_walls(self, cell: Cell, choice: str, new_cell: Cell) -> None:
        if choice == 'N':
            cell.walls -= 1
            new_cell.walls -= 4
        elif choice == 'E':
            cell.walls -= 2
            new_cell.walls -= 8
        elif choice == 'S':
            cell.walls -= 4
            new_cell.walls -= 1
        elif choice == 'W':
            cell.walls -= 8
            new_cell.walls -= 2

    def valid_choice(self, cell_coordinates, choice_coordinates) -> bool:
        try:
            x1, y1 = cell_coordinates
            x2, y2 = choice_coordinates
            if (x1 + x2) < 0 or (y1 + y2) < 0:
                return False
            new_cell: Cell = self.layout[x1 + x2][y1 + y2]
            if new_cell.visited is True:
                return False
            else:
                return True
        except IndexError:
            return False

    def path_direction(self, cell: Cell) -> Cell | None:
        directions = {
            'N': (0, -1),
            'E': (1, 0),
            'S': (0, 1),
            'W': (-1, 0)
            }
        while directions:
            choice = random.choice(list(directions))
            choice_coordinates = directions.pop(choice)
            if self.valid_choice(cell.coordinates, choice_coordinates):
                if self.path_found is False:
                    self.path_cardinal.append(choice)
                x1, y1 = cell.coordinates
                x2, y2 = choice_coordinates
                new_cell = self.layout[x1 + x2][y1 + y2]
                if new_cell.coordinates == self.exit:
                    self.path_found = True
                self.destoy_walls(cell, choice, new_cell)
                return new_cell
        return None

    def solve_maze(self) -> None:
        while self.visited_cells < self.total_cells:
            new_cell = self.path_direction(self.pos)
            if new_cell:
                self.path.append(new_cell)
                new_cell.visited = True
                self.pos = new_cell
                self.visited_cells += 1
            else:
                self.path.remove(self.pos)
                if self.path_found is False:
                    del self.path_cardinal[len(self.path_cardinal) - 1]
                self.pos = self.path[len(self.path) - 1]


def show_maze_coordinates(maze: Maze):
    """test function"""
    for i in range(maze.height):
        row = []
        for j in range(maze.width):
            row.append(maze.layout[j][i].coordinates)
        print(row)


def create_maze_output(maze: Maze) -> Maze:
    maze.output = []
    for i in range(maze.height):
        for j in range(maze.width):
            maze.output.append(maze.layout[j][i].walls)
    return maze


def main() -> None:
    try:
        config = fetch_config("config.txt")
        random.seed(config.SEED)
        maze = Maze(
            config.WIDTH,
            config.HEIGHT,
            config.ENTRY,
            config.EXIT,
            config.PERFECT
            )
        maze.solve_maze()
        create_maze_output(maze)
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()
