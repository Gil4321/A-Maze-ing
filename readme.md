*This project has been created as part of the 42 curriculum by theomart, adghouai.*

# A-Maze-ing

## Description

This project implements a maze generator in Python.
It reads a configuration file, generates a maze using a recursive algorithm, computes the shortest path between an entry and an exit, and writes the result into a file using hexadecimal encoding.

The project also includes a graphical visualization using MiniLibX (MLX), allowing real-time interaction and regeneration of the maze.

---

## Project Architecture

Main file:

* `a_maze_ing.py`

Modules:

* `MazeGenerator`: maze generation logic
* `Cell`: maze cell representation
* `BFS`: shortest path solver
* `parsing_basemodel.py`: configuration parsing
* `test_mlx.py`: graphical rendering (MLX)

---

## Instructions

Prerequisites: Python 3 and the MiniLibX (MLX) library.

To install MLX, use the provided wheel file:

```bash
pip install mlx/mlx-2.2-py3-none-any.whl
```

To run the project:

```bash
python3 a_maze_ing.py config.txt
```

---

## Configuration File

Format: `KEY=VALUE`

### Example

```txt
WIDTH=20
HEIGHT=15
ENTRY=0,0
EXIT=19,14
OUTPUT_FILE=maze.txt
PERFECT=True
SEED=42
```

---

## Maze Generation

The maze is represented as a 2D grid:

```python
layout: list[list[Cell]]
```

Each `Cell` contains:

* coordinates `(x, y)`
* walls (bitmask, initial value = 15)
* visited flag

### Wall Encoding

| Bit | Direction |
| --- | --------- |
| 1   | North     |
| 2   | East      |
| 4   | South     |
| 8   | West      |

---

## Algorithm

### Perfect Maze

Generated using recursive backtracking:

* Random exploration of neighbors
* Wall destruction between adjacent cells
* Full connectivity ensured

Function:

```python
create_perfect_maze(cell)
```

---

### Imperfect Maze

If `PERFECT=False`, extra walls are removed:

```python
create_imperfect_maze()
```

This introduces multiple valid paths.

---

### "42" Pattern

The maze includes a hardcoded "42" pattern:

```python
add_42_pattern()
```

* Applied only if the maze is large enough
* Prevents entry/exit overlap (raises `MazeError`)

---

## Why This Algorithm

Recursive backtracking was chosen because it is a well-established algorithm for generating perfect mazes. It ensures that the maze has exactly one path between any two points, making it suitable for pathfinding problems. Additionally, it is straightforward to implement and provides good performance for maze generation.

---

## Pathfinding

Shortest path computed using BFS:

```python
bfs = BFS(maze)
bfs.solve_maze()
```

The result is stored in:

```python
maze.path
```

---

## Path Encoding

Converted to directions:

```python
cardinal_path(maze)
```

Output format:

```
N E S W
```

---

## Output File

Generated with:

```python
generate_output_file(maze, output, path)
```

### Format

```
<maze grid>

<entry>
<exit>
<path>
```

* Each cell is written as a hexadecimal digit
* Grid is written row by row

---

## MLX Visualization

The graphical interface is launched with:

```python
setup_and_run(maze, regenerator)
```

### Controls

| Key | Action                                |
| --- | ------------------------------------- |
| ESC | Exit program                          |
| 1   | Generate a new maze (no animation)    |
| 2   | Clear current path                    |
| 3   | Redraw current maze                   |
| 4   | Animate path (solution visualization) |
| 5   | Generate a new maze with animation    |

### Behavior Details

* Maze regeneration uses:

```python
maze_regenerator(config)
```

* Path animation is handled dynamically
* Maze can be redrawn or cleared without restarting the program
* Animation state is controlled internally (`_anim_state`)

---

## Reusable Module

The maze generation logic is designed to be reusable.

### Core class

```python
class MazeGenerator
```

### Example usage

```python
from maze_generator import MazeGenerator, BFS

maze = MazeGenerator(
    width=20,
    height=15,
    entry=(0, 0),
    exit=(19, 14),
    perfect=True
)

bfs = BFS(maze)
bfs.solve_maze()

print(maze.path)
```

### Features

* Fully independent maze generation
* Access to internal grid (`layout`)
* Access to computed path (`maze.path`)
* Can be reused in other projects

---

## Error Handling

Custom exception:

```python
class MazeError(Exception)
```

Handled cases:

* Invalid configuration
* Entry/exit conflicts with "42" pattern
* No valid path found
* File errors

---

## Team Roles

* **theomart**

  * MLX graphical interface (`maze_mlx.py`)
  * Rendering and animation system
  * Input handling (keyboard controls)

* **adghouai**

  * Configuration parsing (`parsing_config.py`)
  * Maze generation algorithm
  * BFS pathfinding

## Project Management

### Anticipated Planning

We anticipated dividing the project into two main parts: the core maze generation and pathfinding logic, and the graphical visualization using MLX. Theomart was responsible for the MLX interface, while adghouai handled the generation and parsing.

### How It Evolved

The initial planning held up well throughout the project. We maintained the division of labor, with regular check-ins to ensure compatibility between the components.

### What Worked Well

- Effective communication and clear task assignments.
- Modular design allowed independent development of components.

### What Could Be Improved

- More comprehensive unit testing.
- Earlier integration of the MLX visualization with the maze generation.

### Tools Used

- Git for version control and collaboration.
- VS Code as the primary IDE.
- MiniLibX library for graphical rendering.
- Python's standard library for core functionality.

---


## Resources

* Python documentation: https://docs.python.org/3/
* Maze generation algorithms:

  * Recursive Backtracking
* Graph traversal:

  * Breadth-First Search (BFS)

* AI Usage: AI was used for documentation structure and clarifying algorithm explanations. All outputs were reviewed and validated before integration.


