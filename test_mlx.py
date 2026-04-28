from mlx import Mlx
import os
import math
from maze_generator import MazeGenerator, regen_maze


app = Mlx()
mlx_ptr = app.mlx_init()
WIN_W, WIN_H = 3840, 2160
win_ptr = app.mlx_new_window(mlx_ptr, WIN_W, WIN_H, "A-Mazing")


def close_win(param): os._exit(0)


def key_hook(keycode, param):
    if keycode == 65307:
        os._exit(0)
    if keycode == 49:
        destroymaze()
        generated_maze = regen_maze()
        drawmaze(generated_maze)
    if keycode == 50:
        destroymaze()
        generated_maze = regen_maze()
        draw_maze_iso(generated_maze)
    if keycode == 51:
        destroymaze()
        leprechaun()


app.mlx_hook(win_ptr, 33, 0, close_win, None)
app.mlx_key_hook(win_ptr, key_hook, None)

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


def blend_color(color, t):
    a = (color >> 24) & 0xFF
    r = (color >> 16) & 0xFF
    g = (color >> 8) & 0xFF
    b = color & 0xFF
    f = 0.25 + t * 0.75   # haut du mur = 25% de luminosité
    return (a << 24) | (int(r*f) << 16) | (int(g*f) << 8) | int(b*f)

# flat


def draw_cell(x, y, size, cell):
    # fonction pour le chemin afficher/supprimer et afficher et exit
    px = x * size
    py = y * size
    color = rainbow(x, y)
    thickness = 10

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

# iso


def to_iso(gx, gy, hw, hh, ox, oy):
    return (int(ox + (gx - gy) * hw),
            int(oy + (gx + gy) * hh))


def draw_wall_face(p0, p1, wall_height, color):
    x0, y0 = p0
    x1, y1 = p1
    x2, y2 = x1, y1 - wall_height
    x3, y3 = x0, y0 - wall_height

    y_min = min(y0, y1, y2, y3)
    y_max = max(y0, y1, y2, y3)

    def x_on_seg(xa, ya, xb, yb, y):
        if ya == yb:
            return None
        t = (y - ya) / (yb - ya)
        if 0.0 <= t <= 1.0:
            return xa + t * (xb - xa)
        return None

    def y_on_seg(xa, ya, xb, yb, x):
        if xa == xb:
            return None
        t = (x - xa) / (xb - xa)
        if 0.0 <= t <= 1.0:
            return ya + t * (yb - ya)
        return None

    edges = [(x0, y0, x3, y3), (x3, y3, x2, y2),
             (x2, y2, x1, y1), (x1, y1, x0, y0)]
    bottom_edges = [(x0, y0, x1, y1)]
    top_edges = [(x3, y3, x2, y2)]

    for y in range(y_min, y_max + 1):
        xs = [x_on_seg(xa, ya, xb, yb, y) for xa, ya, xb, yb in edges]
        xs = [v for v in xs if v is not None]
        if len(xs) < 2:
            continue
        x_left = int(min(xs))
        x_right = int(max(xs))

        for x in range(x_left, x_right + 1):
            y_base = next((y_on_seg(xa, ya, xb, yb, x)
                           for xa, ya, xb, yb in bottom_edges
                           if y_on_seg(xa, ya, xb, yb, x) is not None), None)
            y_top = next((y_on_seg(xa, ya, xb, yb, x)
                          for xa, ya, xb, yb in top_edges
                          if y_on_seg(xa, ya, xb, yb, x) is not None), None)

            if y_base is None or y_top is None or y_base == y_top:
                t = 0.5
            else:
                t = (y_base - y) / (y_base - y_top)
                t = max(0.0, min(1.0, t))

            put_pixel(x, y, blend_color(color, t))


def draw_cell_iso(gx, gy, size, cell, ox, oy, wall_height):
    hw = size // 2
    hh = size // 4
    TL = to_iso(gx,   gy,   hw, hh, ox, oy)
    TR = to_iso(gx+1, gy,   hw, hh, ox, oy)
    BR = to_iso(gx+1, gy+1, hw, hh, ox, oy)
    BL = to_iso(gx,   gy+1, hw, hh, ox, oy)
    color = rainbow(gx, gy)

    if cell["N"]:
        draw_wall_face(TL, TR, wall_height, color)
    if cell["S"]:
        draw_wall_face(BL, BR, wall_height, color)
    if cell["W"]:
        draw_wall_face(TL, BL, wall_height, color)
    if cell["E"]:
        draw_wall_face(TR, BR, wall_height, color)


def drawmaze(generated_maze: MazeGenerator):
    size = 50
    for y in range(generated_maze.height):
        for x in range(generated_maze.width):
            cell_value = generated_maze.layout[x][y].walls
            draw_cell(x, y, size, cell_variants[cell_value])

    app.mlx_put_image_to_window(
        mlx_ptr, win_ptr, img_ptr, WIN_W // 2 - generated_maze.width * size // 2, WIN_H // 2 - generated_maze.height * size // 2)
    print("Done !")
    app.mlx_loop(mlx_ptr)


def draw_maze_iso(generated_maze: MazeGenerator):
    size = 40
    wall_height = 18

    ox = WIN_W // 2
    oy = 200

    order = []
    for d in range(generated_maze.width + generated_maze.height - 1):
        for x in range(max(0, d - generated_maze.height + 1), min(d + 1, generated_maze.width)):
            y = d - x
            if 0 <= y < generated_maze.height:
                order.append((x, y))

    for (x, y) in order:
        cell_value = generated_maze.layout[x][y].walls
        draw_cell_iso(
            x, y, size, cell_variants[cell_value], ox, oy, wall_height)

    app.mlx_put_image_to_window(mlx_ptr, win_ptr, img_ptr, 0, 0)


def leprechaun():
    img, w, h = app.mlx_xpm_file_to_image(mlx_ptr, "theomartleprehaun.xpm")
    app.mlx_put_image_to_window(mlx_ptr, win_ptr, img, 0, 0)
    app.mlx_loop(mlx_ptr)


def destroymaze():
    app.mlx_clear_window(mlx_ptr, win_ptr)
    data_addr[:] = b'\x00' * (WIN_W * WIN_H * BPP)


def loop_hook(param):
    return 0
