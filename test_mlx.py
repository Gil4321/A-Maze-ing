from __future__ import annotations
from mlx import Mlx
import os
import math
import random
import numpy as np

app = Mlx()
mlx_ptr = app.mlx_init()
WIN_W, WIN_H = 2160, 1440
win_ptr = app.mlx_new_window(mlx_ptr, WIN_W, WIN_H, "A-Mazing")

img_maze = app.mlx_new_image(mlx_ptr, WIN_W, WIN_H)
data_maze, _, _, _ = app.mlx_get_data_addr(img_maze)

img_path = app.mlx_new_image(mlx_ptr, WIN_W, WIN_H)
data_path, _, _, _ = app.mlx_get_data_addr(img_path)

BPP = 4
LINE_SIZE = WIN_W * BPP
leprechaun = 0

np_maze = np.frombuffer(data_maze, dtype=np.uint8).reshape((WIN_H, WIN_W, BPP))
np_path = np.frombuffer(data_path, dtype=np.uint8).reshape((WIN_H, WIN_W, BPP))

_anim_state = {
    "active": False,
    "segments": [],
    "index": 0,
    "color_offset": 0,
}


def close_win(param): os._exit(0)


def setup_and_run(maze, regenerator):
    state = {
        "maze": maze,
        "regenerator": regenerator,
    }
    app.mlx_hook(win_ptr, 33, 0, close_win, None)
    app.mlx_key_hook(win_ptr, _hook_ref, state)
    app.mlx_loop_hook(mlx_ptr, _loop_hook_ref, state)
    drawmaze(maze, leprechaun)
    app.mlx_loop(mlx_ptr)


def key_hook(keycode, param):
    state = param
    regenerator = state["regenerator"]

    if keycode == 65307:
        os._exit(0)
    if keycode == 49:
        _anim_state["active"] = False
        destroymaze()
        clearpath(state["maze"])
        state["maze"] = regenerator()
        drawmaze(state["maze"], leprechaun = 0)
    if keycode == 50:
        _anim_state["active"] = False
        clearpath(state["maze"])
    if keycode == 51:
        _anim_state["active"] = False
        destroymaze()
        drawmaze(state["maze"], leprechaun = 0)
    if keycode == 52:
        clearpath(state["maze"])
        _start_path_animation(state["maze"], leprechaun)
    if keycode == 53:
        _anim_state["active"] = False
        destroymaze()
        clearpath(state["maze"])
        state["maze"] = regenerator()
        drawmaze(state["maze"], leprechaun = 1)
        _start_path_animation(state["maze"], leprechaun = 1)
   

_hook_ref = key_hook


def drawmaze(generated_maze, leprechaun):
    size = 15
    color = rainbow(random.randint(0, 255), random.randint(0, 255))
    drawentry_exit(generated_maze)
    for y in range(generated_maze.height):
        for x in range(generated_maze.width):
            cell_value = generated_maze.layout[x][y].walls
            if leprechaun == 0:
                draw_cell(x, y, size, cell_variants[cell_value], color)
            else:
                 draw_cell(x, y, size, cell_variants[cell_value], color= rainbow(x,y))


    draw_42(generated_maze)
    offset_x = WIN_W // 2 - generated_maze.width * size // 2
    offset_y = WIN_H // 2 - generated_maze.height * size // 2
    app.mlx_put_image_to_window(mlx_ptr, win_ptr, img_path, 0, 0)
    app.mlx_put_image_to_window(mlx_ptr, win_ptr, img_maze, offset_x, offset_y)
    app.mlx_string_put(
        mlx_ptr, win_ptr,
        WIN_W // 2 - len("Press 1 regenerate | 2 clear path | 3 recolor | 4 animate path | 5 leprechaun") * 5,
        WIN_H // 2 - generated_maze.height * size // 2 - size * 2,
        0xFFFFFFFF, "Press 1 regenerate | 2 clear path | 3 recolor | 4 animate path | 5 leprechaun")
    print("Done!")


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


def rainbow(x, y):
    scale = 0.05
    t = x + y
    r = int(127 + 127 * math.sin(scale * t))
    g = int(127 + 127 * math.sin(scale * t + 2))
    b = int(127 + 127 * math.sin(scale * t + 4))
    return (0xFF << 24) | (r << 16) | (g << 8) | b


def color_to_rgba(color):
    return np.array([
        color & 0xFF,
        (color >> 8) & 0xFF,
        (color >> 16) & 0xFF,
        (color >> 24) & 0xFF,
    ], dtype=np.uint8)


def put_pixel(x, y, color):
    if x < 0 or x >= WIN_W or y < 0 or y >= WIN_H:
        return
    np_maze[y, x] = color_to_rgba(color)


def put_pixel_path(x, y, color):
    if x < 0 or x >= WIN_W or y < 0 or y >= WIN_H:
        return
    np_path[y, x] = color_to_rgba(color)


def fill_rect_maze(x, y, w, h, color):
    x0 = max(x, 0); y0 = max(y, 0)
    x1 = min(x + w, WIN_W); y1 = min(y + h, WIN_H)
    if x1 <= x0 or y1 <= y0:
        return
    np_maze[y0:y1, x0:x1] = color_to_rgba(color)


def fill_rect_path(x, y, w, h, color):
    x0 = max(x, 0); y0 = max(y, 0)
    x1 = min(x + w, WIN_W); y1 = min(y + h, WIN_H)
    if x1 <= x0 or y1 <= y0:
        return
    np_path[y0:y1, x0:x1] = color_to_rgba(color)


def draw_cell(x, y, size, cell, color):
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


def draw_cell_42(x, y, size):
    px = x * size
    py = y * size
    color = 0xFFFFFFFF
    thickness = 4

    fill_rect_maze(px, py, size + thickness, thickness, color)
    fill_rect_maze(px, py + size, size + thickness, thickness, color)
    fill_rect_maze(px, py, thickness, size + thickness, color)
    fill_rect_maze(px + size, py, thickness, size + thickness, color)


def draw_42(generated_maze):
    size = 15
    for y in range(generated_maze.height):
        for x in range(generated_maze.width):
            if generated_maze.layout[x][y].walls == 15:
                draw_cell_42(x, y, size)


def draw_line_thick(x0, y0, x1, y1, color, thickness=3):
    rgba = color_to_rgba(color)
    if x0 == x1:
        ya, yb = (min(y0, y1), max(y0, y1))
        x_a = max(x0 - thickness, 1)
        x_b = min(x0 + thickness + 5, WIN_W)
        ya = max(ya, 0); yb = min(yb + 5, WIN_H)
        np_path[ya:yb, x_a:x_b] = rgba
    else:
        xa, xb = (min(x0, x1), max(x0, x1))
        y_a = max(y0 - thickness, 0)
        y_b = min(y0 + thickness + 5, WIN_H)
        xa = max(xa, 0); xb = min(xb + 6, WIN_W)

        np_path[y_a:y_b, xa:xb] = rgba


def _build_segments(generated_maze, leprechaun):
    size = 15
    wall_gap = 3
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
        else :
            color = rainbow(1, 0)  # dégradé arc-en-ciel le long du chemin

        if x0 == x1:
            if py1 > py0:
                py0 += wall_gap; py1 -= wall_gap
            else:
                py0 -= wall_gap; py1 += wall_gap
        else:  # horizontal
            if px1 > px0:
                px0 += wall_gap; px1 -= wall_gap
            else:
                px0 -= wall_gap; px1 += wall_gap

        segments.append((px0, py0, px1, py1, color))

    return segments


def drawpath(generated_maze,leprechaun):
    segments = _build_segments(generated_maze, leprechaun)
    for px0, py0, px1, py1, color in segments:
        draw_line_thick(px0, py0, px1, py1, color, thickness=2)


def _start_path_animation(maze, leprechaun):
    segments = _build_segments(maze, leprechaun)
    _anim_state["active"] = True
    _anim_state["segments"] = segments
    _anim_state["index"] = 0
    _anim_state["maze"] = maze


def _loop_hook(param):
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


def draw_cell_path(x, y, size, path_color):
    if path_color == 0:
        color = 0xFFF000FF
    elif path_color == 1:
        color = rainbow(x // size, y // size)
    elif path_color == 2:
        color = 0xFF00FF00
    fill_rect_path(x - size // 2, y - size // 2, size, size, color)


def putpath(x, y, size, offset_x, offset_y, path_color):
    px = x * size + offset_x + size // 2
    py = y * size + offset_y + size // 2
    draw_cell_path(px, py, size // 2, path_color)


def drawentry_exit(generated_maze):
    size = 15
    offset_x = WIN_W // 2 - generated_maze.width * size // 2
    offset_y = WIN_H // 2 - generated_maze.height * size // 2
    entry_x, entry_y = generated_maze.entry
    exit_x, exit_y = generated_maze.exit
    putpath(entry_x, entry_y, size, offset_x, offset_y, path_color=0)
    putpath(exit_x, exit_y, size, offset_x, offset_y, path_color=2)



def destroymaze():
    app.mlx_clear_window(mlx_ptr, win_ptr)
    np_maze[:] = 0


def clearpath(maze):
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
        WIN_W // 2 - len("Press 1 regenerate | 2 clear path | 3 recolor | 4 animate path | 5 leprechaun") * 5,
        offset_y - size * 2,
        0xFFFFFFFF, "Press 1 regenerate | 2 clear path | 3 recolor | 4 animate path | 5 leprechaun")


def loop_hook(param):
    return 0