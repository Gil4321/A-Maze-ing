from __future__ import annotations
from mlx import Mlx
import os
import math
import random
import numpy as np
from typing import Any, Callable, TypedDict, TYPE_CHECKING
if TYPE_CHECKING:
    from maze_generator import MazeGenerator

app = Mlx()
mlx_ptr = app.mlx_init()
WIN_W, WIN_H = 3840, 2160
win_ptr = app.mlx_new_window(mlx_ptr, WIN_W, WIN_H, "A-Maze-ing")

img_maze = app.mlx_new_image(mlx_ptr, WIN_W, WIN_H)
data_maze, _, _, _ = app.mlx_get_data_addr(img_maze)

img_path = app.mlx_new_image(mlx_ptr, WIN_W, WIN_H)
data_path, _, _, _ = app.mlx_get_data_addr(img_path)

BPP = 4
LINE_SIZE = WIN_W * BPP
leprechaun = 0

np_maze = np.frombuffer(data_maze, dtype=np.uint8).reshape((WIN_H, WIN_W, BPP))
np_path = np.frombuffer(data_path, dtype=np.uint8).reshape((WIN_H, WIN_W, BPP))


class AnimState(TypedDict, total=False):
    """
    TypedDict representing the current state of the path animation.

    Attributes:
        active: Whether the animation is currently running.
        segments: List of line segments to draw, each as (x0, y0, x1, y1, color).
        index: Index of the next segment to draw in the animation loop.
        color_offset: Unused color offset, reserved for future use.
        maze: The MazeGenerator instance.
    """
    active: bool
    segments: list[tuple[int, int, int, int, int]]
    index: int
    color_offset: int
    maze: MazeGenerator


_anim_state: AnimState = {
    "active": False,
    "segments": [],
    "index": 0,
    "color_offset": 0,
}


def close_win(param: Any) -> None:
    """
    Exit the application immediately.
    """
    os._exit(0)


def setup_and_run(maze: MazeGenerator, regenerator: Callable[[], MazeGenerator]) -> None:
    """
    Initialize hooks and start the MLX event loop.

    Registers the window close, keyboard, and loop hooks, draws the initial maze,
    then hands control over to the MLX main loop.

    Args:
        maze: The initial MazeGenerator instance to display.
        regenerator: A callable that returns a fresh MazeGenerator when invoked,
                     used to regenerate the maze on key press.
    """
    state = {
        "maze": maze,
        "regenerator": regenerator,
    }
    app.mlx_hook(win_ptr, 33, 0, close_win, None)
    app.mlx_key_hook(win_ptr, _hook_ref, state)
    app.mlx_loop_hook(mlx_ptr, _loop_hook_ref, state)
    drawmaze(maze, leprechaun)
    app.mlx_loop(mlx_ptr)


def key_hook(keycode: int, param: dict[str, Any]) -> None:
    """
    Handle keyboard input and trigger the corresponding maze action.

    Key bindings:
        - Escape (65307): Exit the application.
        - 1 (49):         Regenerate and redraw the maze in standard color mode.
        - 2 (50):         Clear the solution path overlay.
        - 3 (51):         Redraw the maze with a new random color.
        - 4 (52):         Clear the path and start the animated path drawing.
        - 5 (53):         Regenerate and redraw the maze in leprechaun (rainbow) color mode.

    Args:
        keycode: The X11 keycode of the pressed key.
        param: Shared state dict containing 'maze' (MazeGenerator) and
               'regenerator' (Callable[[], MazeGenerator]).
    """
    state = param
    regenerator = state["regenerator"]

    if keycode == 65307:
        os._exit(0)
    if keycode == 49:
        _anim_state["active"] = False
        destroymaze()
        clearpath(state["maze"])
        state["maze"] = regenerator()
        drawmaze(state["maze"], leprechaun=0)
    if keycode == 50:
        _anim_state["active"] = False
        clearpath(state["maze"])
    if keycode == 51:
        _anim_state["active"] = False
        destroymaze()
        drawmaze(state["maze"], leprechaun=0)
    if keycode == 52:
        clearpath(state["maze"])
        _start_path_animation(state["maze"], leprechaun)
    if keycode == 53:
        _anim_state["active"] = False
        destroymaze()
        clearpath(state["maze"])
        state["maze"] = regenerator()
        drawmaze(state["maze"], leprechaun=1)


_hook_ref = key_hook


def drawmaze(generated_maze: MazeGenerator, leprechaun: int) -> None:
    """
    Render the full maze in the window.

    Computes the centered position of the maze, picks a base rainbow color,
    draws every cell's walls, overlays the entry/exit markers, prints the
    help text, highlights fully-walled cells with a white border, and
    finally pushes both image buffers to the window.

    Args:
        generated_maze: The MazeGenerator instance whose layout will be drawn.
        leprechaun: Color mode flag. 0 uses a single random rainbow color for
                    all walls; 1 assigns an individual rainbow color to each
                    cell based on its (x, y) position.
    """
    size = 15
    offset_x = WIN_W // 2 - generated_maze.width * size // 2
    offset_y = WIN_H // 2 - generated_maze.height * size // 2
    color = rainbow(random.randint(0, 255), random.randint(0, 255))
    drawentry_exit(generated_maze)
    for y in range(generated_maze.height):
        for x in range(generated_maze.width):
            cell_value = generated_maze.layout[x][y].walls
            if leprechaun == 0:
                draw_cell(x, y, size, cell_variants[cell_value], color)
            else:
                draw_cell(
                    x, y, size, cell_variants[cell_value], color=rainbow(x, y))
    app.mlx_string_put(
        mlx_ptr, win_ptr,
        WIN_W // 2 -
        len("Press 1 regenerate | 2 clear path | 3 recolor | 4 animate path | 5 leprechaun") * 5,
        offset_y - size * 2,
        0xFFFFFFFF, "Press 1 regenerate | 2 clear path | 3 recolor | 4 animate path | 5 leprechaun")
    draw_42(generated_maze)
    app.mlx_put_image_to_window(mlx_ptr, win_ptr, img_path, 0, 0)
    app.mlx_put_image_to_window(mlx_ptr, win_ptr, img_maze, offset_x, offset_y)


cell_variants = {
    0:  {"N": False, "S": False, "E": False, "W": False},
    1:  {"N": True,  "S": False, "E": False, "W": False},
    2:  {"N": False, "S": False, "E": True,  "W": False},
    3:  {"N": True,  "S": False, "E": True,  "W": False},
    4:  {"N": False, "S": True,  "E": False, "W": False},
    5:  {"N": True,  "S": True,  "E": False, "W": False},
    6:  {"N": False, "S": True,  "E": True,  "W": False},
    7:  {"N": True,  "S": True,  "E": True,  "W": False},
    8:  {"N": False, "S": False, "E": False, "W": True},
    9:  {"N": True,  "S": False, "E": False, "W": True},
    10: {"N": False, "S": False, "E": True,  "W": True},
    11: {"N": True,  "S": False, "E": True,  "W": True},
    12: {"N": False, "S": True,  "E": False, "W": True},
    13: {"N": True,  "S": True,  "E": False, "W": True},
    14: {"N": False, "S": True,  "E": True,  "W": True},
    15: {"N": True,  "S": True,  "E": True,  "W": True},
}


def rainbow(x: float, y: float) -> int:
    """
    Compute a smooth rainbow ARGB color from two scalar inputs.

    Uses three phase-shifted sine waves (offset by ~2 radians each) to
    produce continuous RGB cycling across the (x, y) space.

    Args:
        x: First input value contributing to the color phase.
        y: Second input value contributing to the color phase.

    Returns:
        A 32-bit ARGB integer with full opacity (alpha = 0xFF).
    """
    scale = 0.05
    t = x + y
    r = int(127 + 127 * math.sin(scale * t))
    g = int(127 + 127 * math.sin(scale * t + 2))
    b = int(127 + 127 * math.sin(scale * t + 4))
    return (0xFF << 24) | (r << 16) | (g << 8) | b


def color_to_rgba(color: int) -> np.ndarray:
    """
    Unpack a 32-bit ARGB integer into a NumPy RGBA byte array.

    The byte order matches the MLX image buffer layout: [B, G, R, A].

    Args:
        color: A 32-bit integer in 0xAARRGGBB format.

    Returns:
        A NumPy array of shape (4,) with dtype uint8 ordered [B, G, R, A].
    """
    return np.array([
        color & 0xFF,
        (color >> 8) & 0xFF,
        (color >> 16) & 0xFF,
        (color >> 24) & 0xFF,
    ], dtype=np.uint8)


def put_pixel(x: int, y: int, color: int) -> None:
    """
    Write a single pixel to the maze image buffer.

    Silently ignores coordinates outside the window bounds.

    Args:
        x: Horizontal pixel coordinate.
        y: Vertical pixel coordinate.
        color: 32-bit ARGB color value.
    """
    if x < 0 or x >= WIN_W or y < 0 or y >= WIN_H:
        return
    np_maze[y, x] = color_to_rgba(color)


def put_pixel_path(x: int, y: int, color: int) -> None:
    """
    Write a single pixel to the path overlay image buffer.

    Silently ignores coordinates outside the window bounds.

    Args:
        x: Horizontal pixel coordinate.
        y: Vertical pixel coordinate.
        color: 32-bit ARGB color value.
    """
    if x < 0 or x >= WIN_W or y < 0 or y >= WIN_H:
        return
    np_path[y, x] = color_to_rgba(color)


def fill_rect_maze(x: int, y: int, w: int, h: int, color: int) -> None:
    """
    Fill an axis-aligned rectangle in the maze image buffer.

    Clamps the rectangle to the window bounds before writing.

    Args:
        x: Left edge of the rectangle in pixels.
        y: Top edge of the rectangle in pixels.
        w: Width of the rectangle in pixels.
        h: Height of the rectangle in pixels.
        color: 32-bit ARGB fill color.
    """
    x0 = max(x, 0)
    y0 = max(y, 0)
    x1 = min(x + w, WIN_W)
    y1 = min(y + h, WIN_H)
    if x1 <= x0 or y1 <= y0:
        return
    np_maze[y0:y1, x0:x1] = color_to_rgba(color)


def fill_rect_path(x: int, y: int, w: int, h: int, color: int) -> None:
    """
    Fill an axis-aligned rectangle in the path overlay image buffer.

    Clamps the rectangle to the window bounds before writing.

    Args:
        x: Left edge of the rectangle in pixels.
        y: Top edge of the rectangle in pixels.
        w: Width of the rectangle in pixels.
        h: Height of the rectangle in pixels.
        color: 32-bit ARGB fill color.
    """
    x0 = max(x, 0)
    y0 = max(y, 0)
    x1 = min(x + w, WIN_W)
    y1 = min(y + h, WIN_H)
    if x1 <= x0 or y1 <= y0:
        return
    np_path[y0:y1, x0:x1] = color_to_rgba(color)


def draw_cell(x: int, y: int, size: int, cell: dict[str, bool], color: int) -> None:
    """
    Draw the walls of a single maze cell in the maze image buffer.

    Each present wall is rendered as a filled rectangle of the given
    thickness along the corresponding edge of the cell.

    Args:
        x: Grid column index of the cell.
        y: Grid row index of the cell.
        size: Side length of a cell in pixels.
        cell: Dict with boolean flags for each cardinal wall:
              {"N": bool, "S": bool, "E": bool, "W": bool}.
        color: 32-bit ARGB color used for all walls of this cell.
    """
    px = x * size
    py = y * size
    thickness = 3

    if cell["N"]:
        fill_rect_maze(px, py, size + thickness, thickness, color)
    if cell["S"]:
        fill_rect_maze(px, py + size, size + thickness, thickness, color)
    if cell["W"]:
        fill_rect_maze(px, py, thickness, size + thickness, color)
    if cell["E"]:
        fill_rect_maze(px + size, py, thickness, size + thickness, color)


def draw_cell_42(x: int, y: int, size: int) -> None:
    """
    Draw a fully enclosed white cell border (all four walls) in the maze buffer.

    Used to highlight cells whose wall bitmask equals 15 (all walls present),
    visually forming the "42" pattern embedded in the maze.

    Args:
        x: Grid column index of the cell.
        y: Grid row index of the cell.
        size: Side length of a cell in pixels.
    """
    px = x * size
    py = y * size
    color = 0xFFFFFFFF
    thickness = 4

    fill_rect_maze(px, py, size + thickness, thickness, color)
    fill_rect_maze(px, py + size, size + thickness, thickness, color)
    fill_rect_maze(px, py, thickness, size + thickness, color)
    fill_rect_maze(px + size, py, thickness, size + thickness, color)


def draw_42(generated_maze: MazeGenerator) -> None:
    """
    Highlight every fully-walled cell in the maze with a white border.

    Iterates over all cells and calls draw_cell_42 for each cell whose
    wall bitmask is 15 (North + South + East + West all set), creating
    a visible "42" pattern inside the maze.

    Args:
        generated_maze: The MazeGenerator instance to inspect.
    """
    size = 15
    for y in range(generated_maze.height):
        for x in range(generated_maze.width):
            if generated_maze.layout[x][y].walls == 15:
                draw_cell_42(x, y, size)


def draw_line_thick(x0: int, y0: int, x1: int, y1: int, color: int, thickness: int = 3) -> None:
    """
    Draw a thick axis-aligned line segment in the path overlay buffer.

    Only horizontal and vertical lines are supported. The line is
    expanded symmetrically by `thickness` pixels on each side and
    written as a filled rectangle slice into np_path.

    Args:
        x0: X coordinate of the start point.
        y0: Y coordinate of the start point.
        x1: X coordinate of the end point.
        y1: Y coordinate of the end point.
        color: 32-bit ARGB color of the line.
        thickness: Half-width of the line in pixels (default 3).
    """
    rgba = color_to_rgba(color)
    if x0 == x1:
        ya, yb = (min(y0, y1), max(y0, y1))
        x_a = max(x0 - thickness, 0)
        x_b = min(x0 + thickness + 5, WIN_W)
        ya = max(ya, 0)
        yb = min(yb + 5, WIN_H)
        np_path[ya:yb, x_a:x_b] = rgba
    else:
        xa, xb = (min(x0, x1), max(x0, x1))
        y_a = max(y0 - thickness, 0)
        y_b = min(y0 + thickness + 5, WIN_H)
        xa = max(xa, 0)
        xb = min(xb + 6, WIN_W)
        np_path[y_a:y_b, xa:xb] = rgba


def _build_segments(generated_maze: MazeGenerator, leprechaun: int) -> list[tuple[int, int, int, int, int]]:
    """
    Convert the maze solution path into a list of drawable line segments.

    Each consecutive pair of cells in the path is translated to pixel
    coordinates (centered on each cell), slightly inset from the walls,
    and paired with a color derived from the step index or position.

    Args:
        generated_maze: The MazeGenerator whose .path attribute contains
                        the solution as a sequence of (col, row) tuples.
        leprechaun: Color mode flag. 0 applies a progressive rainbow color
                    based on the segment index; 1 uses a fixed rainbow value.

    Returns:
        A list of (x0, y0, x1, y1, color) tuples ready for draw_line_thick.
    """
    size = 15
    wall_gap = 0
    offset_x = WIN_W // 2 - generated_maze.width * size // 2
    offset_y = WIN_H // 2 - generated_maze.height * size // 2
    path = list(generated_maze.path)
    segments = []

    for i in range(len(path) - 1):
        x0, y0 = path[i]
        x1, y1 = path[i + 1]
        px0 = x0 * size + size // 2 + offset_x
        py0 = y0 * size + size // 2 + offset_y
        px1 = x1 * size + size // 2 + offset_x
        py1 = y1 * size + size // 2 + offset_y

        if leprechaun == 0:
            color = rainbow(i * 0.25, 0)
        else:
            color = rainbow(1, 0)

        if x0 == x1:
            if py1 > py0:
                py0 += wall_gap
                py1 -= wall_gap
            else:
                py0 -= wall_gap
                py1 += wall_gap
        else:
            if px1 > px0:
                px0 += wall_gap
                px1 -= wall_gap
            else:
                px0 -= wall_gap
                px1 += wall_gap

        segments.append((px0, py0, px1, py1, color))

    return segments


def drawpath(generated_maze: MazeGenerator, leprechaun: int) -> None:
    """
    Draw the complete solution path instantly in the path overlay buffer.

    Builds all segments and renders them in a single pass without animation.

    Args:
        generated_maze: The MazeGenerator instance containing the solution path.
        leprechaun: Color mode flag forwarded to _build_segments.
    """
    segments = _build_segments(generated_maze, leprechaun)
    for px0, py0, px1, py1, color in segments:
        draw_line_thick(px0, py0, px1, py1, color, thickness=3)


def _start_path_animation(maze: MazeGenerator, leprechaun: int) -> None:
    """
    Initialize the animation state to progressively draw the solution path.

    Populates _anim_state with the pre-built segment list and resets the
    index to 0. The actual drawing is performed incrementally by _loop_hook
    on each frame of the MLX event loop.

    Args:
        maze: The MazeGenerator instance whose solution path will be animated.
        leprechaun: Color mode flag forwarded to _build_segments.
    """
    segments = _build_segments(maze, leprechaun)
    _anim_state["active"] = True
    _anim_state["segments"] = segments
    _anim_state["index"] = 0
    _anim_state["maze"] = maze


def _loop_hook(param: dict[str, Any]) -> int:
    """
    MLX loop callback that advances the path animation by one batch per frame.

    Called every frame by the MLX event loop. If the animation is active,
    draws up to `step` segments per call (scaled to ~200 total frames),
    then pushes both image buffers to the window. Deactivates automatically
    when all segments have been drawn.

    Args:
        param: Unused shared state dict (animation state is read from
               the module-level _anim_state).

    Returns:
        0 in all cases, as required by the MLX loop hook signature.
    """
    if not _anim_state["active"]:
        return 0
    maze = _anim_state["maze"]
    segments = _anim_state["segments"]
    idx = _anim_state["index"]

    if idx >= len(segments):
        _anim_state["active"] = False
        return 0

    step = max(1, len(segments) // 200)
    for _ in range(step):
        if idx >= len(segments):
            break
        px0, py0, px1, py1, color = segments[idx]
        draw_line_thick(px0, py0, px1, py1, color, thickness=2)
        idx += 1

    _anim_state["index"] = idx

    size = 15
    offset_x = WIN_W // 2 - maze.width * size // 2
    offset_y = WIN_H // 2 - maze.height * size // 2
    app.mlx_put_image_to_window(mlx_ptr, win_ptr, img_path, 0, 0)
    app.mlx_put_image_to_window(mlx_ptr, win_ptr, img_maze, offset_x, offset_y)
    return 0


_loop_hook_ref = _loop_hook


def draw_cell_path(x: int, y: int, size: int, path_color: int) -> None:
    """
    Fill a small square marker in the path overlay at the given pixel position.

    The color is determined by the path_color mode:
        - 0: Solid yellow (0xFFF000FF) — used for the entry cell.
        - 1: Rainbow color based on grid position.
        - 2: Solid green (0xFF00FF00) — used for the exit cell.

    Args:
        x: Center X pixel coordinate of the marker.
        y: Center Y pixel coordinate of the marker.
        size: Half-side length of the square marker in pixels.
        path_color: Integer mode selector (0, 1, or 2).
    """
    if path_color == 0:
        color = 0xFFF000FF
    elif path_color == 1:
        color = rainbow(x // size, y // size)
    elif path_color == 2:
        color = 0xFF00FF00
    fill_rect_path(x - size // 2, y - size // 2, size, size, color)


def putpath(x: int, y: int, size: int, offset_x: int, offset_y: int, path_color: int) -> None:
    """
    Draw a colored marker at a maze cell's center in the path overlay.

    Converts grid coordinates to pixel coordinates (accounting for the
    global window offset) and delegates to draw_cell_path.

    Args:
        x: Grid column index of the cell.
        y: Grid row index of the cell.
        size: Cell size in pixels (marker radius will be size // 2).
        offset_x: Horizontal pixel offset of the maze's top-left corner.
        offset_y: Vertical pixel offset of the maze's top-left corner.
        path_color: Color mode forwarded to draw_cell_path (0, 1, or 2).
    """
    px = x * size + offset_x + size // 2
    py = y * size + offset_y + size // 2
    draw_cell_path(px, py, size // 2, path_color)


def drawentry_exit(generated_maze: MazeGenerator) -> None:
    """
    Draw colored markers for the maze entry and exit cells.

    The entry cell is drawn in yellow (path_color=0) and the exit cell
    in green (path_color=2), centered on their respective grid positions.

    Args:
        generated_maze: The MazeGenerator instance providing .entry and
                        .exit as (col, row) tuples.
    """
    size = 15
    offset_x = WIN_W // 2 - generated_maze.width * size // 2
    offset_y = WIN_H // 2 - generated_maze.height * size // 2
    entry_x, entry_y = generated_maze.entry
    exit_x, exit_y = generated_maze.exit
    putpath(entry_x, entry_y, size, offset_x, offset_y, path_color=0)
    putpath(exit_x, exit_y, size, offset_x, offset_y, path_color=2)


def destroymaze() -> None:
    """
    Clear both the window and the maze image buffer.

    Calls mlx_clear_window to erase the visible window content and
    zeroes out np_maze so the next drawmaze call starts from a blank state.
    """
    app.mlx_clear_window(mlx_ptr, win_ptr)
    np_maze[:] = 0


def clearpath(maze: MazeGenerator) -> None:
    """
    Clear the path overlay and redraw the static maze elements.

    Zeroes np_path, clears the window, re-draws the entry/exit markers,
    redraws the help text, and pushes both image buffers back to the window.

    Args:
        maze: The MazeGenerator instance used to recompute offset and
              re-draw the entry/exit markers.
    """
    np_path[:] = 0
    size = 15
    offset_x = WIN_W // 2 - maze.width * size // 2
    offset_y = WIN_H // 2 - maze.height * size // 2
    app.mlx_clear_window(mlx_ptr, win_ptr)
    drawentry_exit(maze)
    app.mlx_put_image_to_window(mlx_ptr, win_ptr, img_maze, offset_x, offset_y)
    app.mlx_put_image_to_window(mlx_ptr, win_ptr, img_path, 0, 0)
    app.mlx_string_put(
        mlx_ptr, win_ptr,
        WIN_W // 2 -
        len("Press 1 regenerate | 2 clear path | 3 recolor | 4 animate path | 5 leprechaun") * 5,
        offset_y - size * 2,
        0xFFFFFFFF, "Press 1 regenerate | 2 clear path | 3 recolor | 4 animate path | 5 leprechaun")


def loop_hook(param: Any) -> int:
    """
    Placeholder MLX loop hook that performs no action.

    Satisfies the MLX loop hook signature requirement without any side
    effects. Can be used as a no-op fallback when no per-frame logic is needed.

    Args:
        param: Unused parameter passed by the MLX event loop.

    Returns:
        0, as required by the MLX loop hook contract.
    """
    return 0
