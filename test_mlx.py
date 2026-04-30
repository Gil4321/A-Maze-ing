from __future__ import annotations
from mlx import Mlx
import os
import math
import random

app = Mlx()
mlx_ptr = app.mlx_init()
WIN_W, WIN_H = 3840, 2160
win_ptr = app.mlx_new_window(mlx_ptr, WIN_W, WIN_H, "A-Mazing")

img_maze = app.mlx_new_image(mlx_ptr, WIN_W, WIN_H)
data_maze, _, _, _ = app.mlx_get_data_addr(img_maze)

img_path = app.mlx_new_image(mlx_ptr, WIN_W, WIN_H)
data_path, _, _, _ = app.mlx_get_data_addr(img_path)


def close_win(param): os._exit(0)


def setup_and_run(maze, regenerator):
    state = {
        "maze": maze,
        "regenerator": regenerator,
    }
    app.mlx_hook(win_ptr, 33, 0, close_win, None)
    app.mlx_key_hook(win_ptr, _hook_ref, state)  # state global via _hook_ref
    drawmaze(maze)  # premier affichage


def key_hook(keycode, param):
    state = param
    regenerator = state["regenerator"]

    if keycode == 65307:
        os._exit(0)
    if keycode == 49:
        destroymaze()
        state["maze"] = regenerator()
        drawmaze(state["maze"])
    if keycode == 50:
        clearpath(state["maze"])
    if keycode == 51:
        destroymaze()
        drawmaze(state["maze"])


_hook_ref = key_hook


def drawmaze(generated_maze: MazeGenerator):
    size = 15
    color = rainbow(random.randint(0, 255), random.randint(0, 255))
    drawentry_exit(generated_maze)
    drawpath(generated_maze)
    for y in range(generated_maze.height):
        for x in range(generated_maze.width):
            cell_value = generated_maze.layout[x][y].walls
            draw_cell(x, y, size, cell_variants[cell_value], color)
    app.mlx_put_image_to_window(
        mlx_ptr, win_ptr, img_maze, WIN_W // 2 - generated_maze.width * size // 2, WIN_H // 2 - generated_maze.height * size // 2)
    print("Done !")
    app.mlx_string_put(
        mlx_ptr, win_ptr, WIN_W // 2 - len("Press 1 ro regenerate, 2 to clear path, 3 to change color") * 5,  WIN_H // 2 - generated_maze.height * size // 2 - size * 2, 0xFFFFFFFF, "Press 1 ro regenerate, 2 to clear path, 3 to change color")
    draw_42(generated_maze)
    app.mlx_loop(mlx_ptr)


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

img_ptr = app.mlx_new_image(mlx_ptr, WIN_W, WIN_H)
data_addr, bpp, line_size, endian = app.mlx_get_data_addr(img_ptr)
BPP = 4
LINE_SIZE = WIN_W * BPP


def put_pixel(x, y, color):
    if x < 0 or x >= WIN_W or y < 0 or y >= WIN_H:
        return
    off = y * LINE_SIZE + x * BPP
    data_addr[off] = color & 0xFF
    data_addr[off + 1] = (color >> 8) & 0xFF
    data_addr[off + 2] = (color >> 16) & 0xFF
    data_addr[off + 3] = (color >> 24) & 0xFF


def rainbow(x, y):
    scale = 0.05
    t = x + y
    r = int(127 + 127 * math.sin(scale * t))
    g = int(127 + 127 * math.sin(scale * t + 2))
    b = int(127 + 127 * math.sin(scale * t + 4))
    return (0xFF << 24) | (r << 16) | (g << 8) | b


def draw_cell(x, y, size, cell, color):
    # fonction pour le chemin afficher/supprimer et afficher et exit
    px = x * size
    py = y * size
    thickness = 3

    if cell["N"]:
        for t in range(thickness):
            for i in range(size + thickness):
                put_pixel(px + i, py + t, color)
    if cell["S"]:
        for t in range(thickness):
            for i in range(size + thickness):
                put_pixel(px + i, py + size + t, color)
    if cell["W"]:
        for t in range(thickness):
            for i in range(size + thickness):
                put_pixel(px + t, py + i, color)
    if cell["E"]:
        for t in range(thickness):
            for i in range(size + thickness):
                put_pixel(px + size + t, py + i, color)


def draw_cell_42(x, y, size, cell):
    # fonction pour le chemin afficher/supprimer et afficher et exit
    px = x * size
    py = y * size
    color = 0xFFFFFFFF
    thickness = 4

    for t in range(thickness):
        for i in range(size + thickness):
            put_pixel(px + i, py + t, color)

    for t in range(thickness):
        for i in range(size + thickness):
            put_pixel(px + i, py + size + t, color)

    for t in range(thickness):
        for i in range(size + thickness):
            put_pixel(px + t, py + i, color)

    for t in range(thickness):
        for i in range(size + thickness):
            put_pixel(px + size + t, py + i, color)


def draw_cell_path(x, y, size, path_color):
    if path_color == 0:
        color = 0xFFF000FF
    elif path_color == 1:
        color = rainbow(x // size, y // size)
    elif path_color == 2:
        color = 0xFF00FF00
    for t in range(size + 1):
        for i in range(size + size // 2):
            put_pixel(x - size // 2 + i, y - t, color)
            put_pixel(x - size // 2 + i, y + t, color)
            put_pixel(x - t, y - size // 2 + i, color)
            put_pixel(x + t, y - size // 2 + i, color)


def draw_42(generated_maze: MazeGenerator):
    size = 15
    for y in range(generated_maze.height):
        for x in range(generated_maze.width):
            cell_value = generated_maze.layout[x][y].walls
            if cell_value == 15:
                draw_cell_42(x, y, size, cell_variants[cell_value])

    app.mlx_put_image_to_window(
        mlx_ptr, win_ptr, img_ptr, WIN_W // 2 - generated_maze.width * size // 2, WIN_H // 2 - generated_maze.height * size // 2)


def putpath(x, y, size, offset_x, offset_y, path_color):
    px = x * size + offset_x + size // 2
    py = y * size + offset_y + size // 2

    draw_cell_path(px, py, size // 2, path_color)


def drawpath(generated_maze: MazeGenerator):
    size = 15
    offset_x = 0
    offset_y = 0
    path_coords = generated_maze.path
    print(f"set coordinates: {path_coords}")
    print(f"list coordinates: {generated_maze.path}")
    for y in range(generated_maze.height):
        for x in range(generated_maze.width):
            if (x, y) in path_coords:
                print(f"Drawing path cell at ({x}, {y})")
                putpath(x, y, size, offset_x, offset_y, path_color=1)


def drawentry_exit(generated_maze: MazeGenerator):
    size = 15
    offset_x = 0
    offset_y = 0
    entry_x, entry_y = generated_maze.entry
    exit_x, exit_y = generated_maze.exit
    putpath(entry_x, entry_y, size, offset_x, offset_y, path_color=0)
    putpath(exit_x, exit_y, size, offset_x, offset_y, path_color=2)


def destroymaze():
    app.mlx_clear_window(mlx_ptr, win_ptr)
    data_addr[:] = b'\x00' * (WIN_W * WIN_H * BPP)


def clearpath():
    data_path[:] = b'\x00' * (WIN_W * WIN_H * BPP)  # efface seulement img_path
    app.mlx_put_image_to_window(mlx_ptr, win_ptr, img_path, 0, 0)


def loop_hook(param):
    return 0
