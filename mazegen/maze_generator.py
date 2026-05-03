import random
import sys
sys.setrecursionlimit(99999999)


class MazeError(Exception):
    """Custom exception raised for errors during maze generation or solving."""
    def __init__(self, error: str) -> None:
        super().__init__(error)


class Cell:
    """Represents a single cell in the maze grid."""

    def __init__(self, coordinates: tuple[int, int]) -> None:
        """
        Args:
            coordinates (tuple[int, int]): (x y) position of the cell
            in the maze.
            walls (int): 4-bit integer encoding the presence of walls.
                Bits represent walls in the order:
                WEST (8), SOUTH (4), EAST (2), NORTH (1).
                A bit set to 1 means the wall is present.
                Default value 15 (1111) means all four walls are present.
            visited (bool): Indicates whether the cell has been visited
                during maze generation or solving.
        """
        self.coordinates = coordinates
        self.walls: int = 15
        self.visited: bool = False


class MazeGenerator:
    """
    Represents the maze.
    It also contains the shortest path available to go from entry to exit
    """
    def __init__(
            self,
            width: int,
            height: int,
            entry: tuple[int, int],
            exit: tuple[int, int],
            perfect: bool,
            seed: str | None
    ) -> None:
        """
        Args:
            width (int): Width of the maze.
            height (int): Height of the maze.
            entry (tuple[int, int]): Starting coordinates of the maze.
            exit (tuple[int, int]): Exit coordinates of the maze.
            perfect (bool): If True, generates a perfect maze
                            (only one optimal path from entry to exit).

                            If False, remove additional walls from an already
                            generated perfect maze which means that multiple
                            paths are possible.
            seed (str | None): Seed for random number generation.

        The constructor:
            - Initializes the grid of cells.
            - Optionally embeds a "42" pattern in the maze.
            - Generates a perfect maze using DFS.
            - Optionally introduces imperfections if the maze is imperfect.
            - Solves the maze using BFS to find the shortest path.
        """
        random.seed(seed)
        self.width = width
        self.height = height
        self.entry = entry
        self.exit = exit
        self.layout: list[list[Cell]] = self.initialize_layout(width, height)
        if width >= 8 and height >= 6:
            self.add_42_pattern()
        else:
            sys.stderr.write("Could not add 42 pattern, maze is too small")
        x, y = entry
        self.create_perfect_maze(self.layout[x][y])
        if perfect is False:
            self.create_imperfect_maze()
        bfs = BFS(self)
        self.path: list[tuple[int, int]] = bfs.solve_maze()

    @staticmethod
    def initialize_layout(x: int, y: int) -> list[list[Cell]]:
        """
        Creates a 2D grid of Cell objects.

        Args:
            x (int): Width of the maze.
            y (int): Height of the maze.

        Returns:
            list[list[Cell]]: A 2D array representing the maze layout,
            where each element is a Cell initialized with all walls present.
        """
        layout = []
        for i in range(x):
            vertical_row = [Cell((i, j)) for j in range(y)]
            layout.append(vertical_row)
        return layout

    def add_42_pattern(self) -> None:
        """
        Marks a predefined "42" pattern in the maze as already visited.

        This prevents the maze generation algorithm from modifying these cells,
        effectively embedding a fixed shape into the maze.

        Raises:
            MazeError: If the entry or exit point lies within the pattern.
        """
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
        """
        Removes the wall between two adjacent cells.

        Args:
            cell (Cell): Current cell.
            new_cell (Cell): Adjacent cell.
            choice (tuple[int, int]): Direction vector indicating the neighbor
            coordinates by adding them to the current cell coordinates.

        The wall encoding uses 4 bits:
            WEST (8), SOUTH (4), EAST (2), NORTH (1).
        This method updates both cells walls value.
        """
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

    def valid_neighbor_perfect(
            self,
            cell: Cell,
            random_direction: tuple[int, int]
    ) -> bool:
        """
        Checks whether a neighboring cell can be visited during perfect maze
        generation.

        Args:
            cell (Cell): Current cell.
            random_direction (tuple[int, int]): Direction to check.

        Returns:
            bool: True if the neighbor exists and has not been visited.
        """
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
        """
        Computes all valid directions from the current cell in random order.

        Args:
            cell (Cell): Current cell.

        Returns:
            list[tuple[int, int]]: List of valid direction vectors leading
            to unvisited neighboring cells.
        """
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
            if self.valid_neighbor_perfect(cell, random_direction):
                availabe_paths.append(random_direction)
        return availabe_paths

    def create_perfect_maze(self, cell: Cell) -> None:
        """
        Generates a perfect maze using recursive depth-first search (DFS).

        Args:
            cell (Cell): Starting cell.

        The algorithm:
            - Marks the current cell as visited
            - Compute every available directions from the current cell
            and stores it in a list
            - Explores unvisited neighbors by using vectors from the list
            - Removes walls between the current cell and the neighoring cells
            - Calls itself back with the neighboring cell as argument
        """
        cell.visited = True
        available_paths = self.path_directions(cell)
        for path in available_paths:
            x1, y1 = cell.coordinates
            x2, y2 = path
            new_cell = self.layout[x1 + x2][y1 + y2]
            if not new_cell.visited:
                self.destoy_walls(cell, new_cell, path)
            self.create_perfect_maze(new_cell)

    def create_imperfect_maze(self) -> None:
        """
        Introduces loops into the maze by randomly removing a wall in a 3 x 3
        square if possible. (if x2 or y2 reaches a value greater than the
        width or height of the maze the wall will be removed in a smaller
        perimeter. e.g: width == 2 and height == 3, the permimeter will
        be a 2 x 3 rectangle).

        This breaks the "perfect maze" property and allows multiple paths
        to go from a cell A to another cell B.
        """
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

    def find_random_valid_cell(
            self,
            x_range: list[int],
            y_range: list[int]
            ) -> None:
        """
        Selects a random cell by using the coordinates in a list generated
        by using both arguments and attempts to remove a wall.

        Args:
            x_range (list[int]): Range of x indices.
            y_range (list[int]): Range of y indices.

        The loop continues until a valid cell is found
        or every coordinates in the list is tested.
        """
        found_valid_cell = False
        coordinates_values = []
        for x in x_range:
            for y in y_range:
                coordinates_values.append((x, y))
        while coordinates_values and found_valid_cell is False:
            coordinates = random.choice(coordinates_values)
            coordinates_values.remove(coordinates)
            x, y = coordinates
            cell: Cell = self.layout[x][y]
            if cell.walls != 15:
                found_valid_cell = self.destroy_random_wall(cell)

    def destroy_random_wall(self, cell: Cell) -> bool:
        """
        Computes a list of valid walls to remove from the cell and select
        a random value from this list. It will then call
        "valid_neightbor_imperfect" to validate that the wall can be removed
        from both the cell and the neightboring cell corresponding to the
        random choice. eg: if the wall == 8 (WEST) it will check if the
        eastern cell from the cell is valid.

        Args:
            cell (Cell): The cell to modify.

        Returns:
            bool: True if a wall was successfully removed, False otherwise.
        """
        wall_values = [8, 4, 2, 1]
        x, y = cell.coordinates
        if x == 0:
            wall_values.remove(8)
        if x == self.width - 1:
            wall_values.remove(2)
        if y == 0:
            wall_values.remove(1)
        if y == self.height - 1:
            wall_values.remove(4)
        while wall_values:
            random_wall = random.choice(wall_values)
            wall_values.remove(random_wall)
            if random_wall & cell.walls:
                if self.valid_neighbor_imperfect(cell, random_wall):
                    return True
        return False

    def valid_neighbor_imperfect(self, cell: Cell, wall: int) -> bool:
        """
        Validates and removes a wall between a cell and its neighbor
        if the neighbor is a valid cell to remove a wall from.

        Args:
            cell (Cell): Current cell.
            wall (int): Wall bit to remove.

        Returns:
            bool: True if the wall was removed successfully.

        If the neighbor is valid, the method updates both
        the current cell and its neighbor walls values.
        """
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


class BFS:
    """
    Breadth-First Search solver for the maze.

    This class finds a path from the entry to the exit
    using BFS, ensuring the shortest path is found.
    """
    def __init__(self, maze: MazeGenerator) -> None:
        """
        Initializes the BFS solver.

        Args:
            maze (MazeGenerator): The maze to solve.

        Resets all cells' visited state to False before solving.
        """
        self.path_list: list[list[tuple[int, int]]] = []
        for row in maze.layout:
            for cell in row:
                cell.visited = False
        self.maze = maze

    def find_directions(self, cell: Cell) -> list[tuple[int, int]]:
        """
        Finds all accessible neighboring cells from the current cell.

        Args:
            cell (Cell): Current cell.

        Returns:
            list[tuple[int, int]]: Coordinates of reachable neighbors
            (i.e., no wall between cells and not yet visited).
        """
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
        """
        Initializes BFS paths starting from the maze entry.

        Creates initial paths for each accessible neighbor of the entry cell.
        those paths are lists of coordinates which are the positions of the
        cells in the maze.
        """
        x, y = self.maze.entry
        starting_cell = self.maze.layout[x][y]
        starting_cell.visited = True
        valid_coordinates = self.find_directions(starting_cell)
        for coordinates in valid_coordinates:
            self.path_list.append([coordinates])

    def solve_maze(self) -> list[tuple[int, int]]:
        """
        Solves the maze using Breadth-First Search (BFS).

        Finds the shortest path from entry to exit.

        Continually iterates in the path list, uses the last coordinates
        from a path to get the next coordinates to add to the path,
        then it adds them with the path to get the updated path or paths.
        It stops when the exit coordinates are found and returns the shortest
        path.

        Returns:
            list[tuple[int, int]]: Coordinates list containing the shortest
            path to take to go from entry to exit. Entry and exit coordinates
            are not included.

        Raises:
            MazeError: If no path to the exit exists.
        """
        self.initialize_entry_paths()
        while self.path_list:
            for path in self.path_list:
                x, y = path[-1]
                cell: Cell = self.maze.layout[x][y]
                cell.visited = True
                valid_coordinates = self.find_directions(cell)
                for coordinates in valid_coordinates:
                    if coordinates == self.maze.exit:
                        return path
                    self.path_list.append(path + [coordinates])
                self.path_list.remove(path)
        raise MazeError("No path to exit found")
