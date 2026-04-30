from mlx import Mlx
import os
import math
from maze_generator import MazeGenerator, regen_maze
import random

app = Mlx()
mlx_ptr = app.mlx_init()
WIN_W, WIN_H = 3840, 2160
win_ptr = app.mlx_new_window(mlx_ptr, WIN_W, WIN_H, "A-Mazing")
generated_maze =


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
    if keycode == 52:
        generated_maze = regen_maze()
        drawpath(generated_maze)
    if keycode == 53:
        clearpath(generated_maze)


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
    thickness = 3

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


def draw_cell_path(x, y, size):
    color = rainbow(x // size, y // size)
    for t in range(size + 1):
        for i in range(size + size // 2):
            put_pixel(x - size // 2 + i, y - t, color)
            put_pixel(x - size // 2 + i, y + t, color)
            put_pixel(x - t, y - size // 2 + i, color)
            put_pixel(x + t, y - size // 2 + i, color)


def draw_cell_path_black(x, y, size):
    color = 0x000000
    for t in range(size + 1):
        for i in range(size + size // 2):
            put_pixel(x - size // 2 + i, y - t, color)
            put_pixel(x - size // 2 + i, y + t, color)
            put_pixel(x - t, y - size // 2 + i, color)
            put_pixel(x + t, y - size // 2 + i, color)

# iso


def to_iso(gx, gy, hw, hh, ox, oy):
    return (int(ox + (gx - gy) * hw),
            int(oy + (gx + gy) * hh))


def drawpath_iso(generated_maze, size, ox, oy, wall_height, path_coords):
    hw = size // 2
    hh = size // 4
    for y in range(generated_maze.height):
        for x in range(generated_maze.width):
            if (x, y) in path_coords:
                # On dessine un losange plein légèrement lumineux sur ces cellules
                TL = to_iso(x,   y,   hw, hh, ox, oy)
                TR = to_iso(x-1, y,   hw, hh, ox, oy)
                BR = to_iso(x-1, y-1, hw, hh, ox, oy)
                BL = to_iso(x,   y-1, hw, hh, ox, oy)

                color = rainbow(x, y)
                points = [TL, TR, BR, BL]
                y_min = min(p[1] for p in points)
                y_max = max(p[1] for p in points)
                edges = [
                    (TL, TR), (TR, BR), (BR, BL), (BL, TL)
                ]

                def x_on_seg_42(xa, ya, xb, yb, scan_y):
                    if ya == yb:
                        return None
                    t = (scan_y - ya) / (yb - ya)
                    if 0.0 <= t <= 1.0:
                        return xa + t * (xb - xa)
                    return None
                for scan_y in range(y_min, y_max + 1):
                    xs = [x_on_seg_42(xa, ya, xb, yb, scan_y)
                          for (xa, ya), (xb, yb) in edges]
                    xs = [v for v in xs if v is not None]
                    if len(xs) < 2:
                        continue
                    for px in range(int(min(xs)), int(max(xs)) - 1):
                        put_pixel(px, scan_y, color)


def draw_42_iso(generated_maze, size, ox, oy, wall_height):
    """Dessine les cellules walls==15 en iso (équivalent draw_42 pour la vue flat)."""
    hw = size // 2
    hh = size // 4
    for y in range(generated_maze.height):
        for x in range(generated_maze.width):
            if generated_maze.layout[x][y].walls == 15:
                # On dessine un losange plein légèrement lumineux sur ces cellules
                TL = to_iso(x,   y,   hw, hh, ox, oy)
                TR = to_iso(x-1, y,   hw, hh, ox, oy)
                BR = to_iso(x-1, y-1, hw, hh, ox, oy)
                BL = to_iso(x,   y-1, hw, hh, ox, oy)

                color = 0xFFFFFFFF  # blanc comme draw_42 flat
                # Remplissage du losange par scanline
                points = [TL, TR, BR, BL]
                y_min = min(p[1] for p in points)
                y_max = max(p[1] for p in points)
                edges = [
                    (TL, TR), (TR, BR), (BR, BL), (BL, TL)
                ]

                def x_on_seg_42(xa, ya, xb, yb, scan_y):
                    if ya == yb:
                        return None
                    t = (scan_y - ya) / (yb - ya)
                    if 0.0 <= t <= 1.0:
                        return xa + t * (xb - xa)
                    return None
                for scan_y in range(y_min, y_max + 1):
                    xs = [x_on_seg_42(xa, ya, xb, yb, scan_y)
                          for (xa, ya), (xb, yb) in edges]
                    xs = [v for v in xs if v is not None]
                    if len(xs) < 2:
                        continue
                    for px in range(int(min(xs)), int(max(xs)) + 1):
                        put_pixel(px, scan_y, color)


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


def draw_cell_iso(gx, gy, size, cell, ox, oy, wall_height, color):
    hw = size // 2
    hh = size // 4
    TL = to_iso(gx,   gy,   hw, hh, ox, oy)
    TR = to_iso(gx+1, gy,   hw, hh, ox, oy)
    BR = to_iso(gx+1, gy+1, hw, hh, ox, oy)
    BL = to_iso(gx,   gy+1, hw, hh, ox, oy)

    if cell["N"]:
        draw_wall_face(TL, TR, wall_height, color)
    if cell["S"]:
        draw_wall_face(BL, BR, wall_height, color)
    if cell["W"]:
        draw_wall_face(TL, BL, wall_height, color)
    if cell["E"]:
        draw_wall_face(TR, BR, wall_height, color)


def draw_42(generated_maze: MazeGenerator):
    size = 15
    for y in range(generated_maze.height):
        for x in range(generated_maze.width):
            cell_value = generated_maze.layout[x][y].walls
            if cell_value == 15:
                draw_cell_42(x, y, size, cell_variants[cell_value])

    app.mlx_put_image_to_window(
        mlx_ptr, win_ptr, img_ptr, WIN_W // 2 - generated_maze.width * size // 2, WIN_H // 2 - generated_maze.height * size // 2)


def drawmaze(generated_maze: MazeGenerator):
    size = 15
    color = rainbow(random.randint(0, 255), random.randint(0, 255))
    drawpath(generated_maze)
    for y in range(generated_maze.height):
        for x in range(generated_maze.width):
            cell_value = generated_maze.layout[x][y].walls
            draw_cell(x, y, size, cell_variants[cell_value], color)
    app.mlx_put_image_to_window(
        mlx_ptr, win_ptr, img_ptr, WIN_W // 2 - generated_maze.width * size // 2, WIN_H // 2 - generated_maze.height * size // 2)
    print("Done !")
    app.mlx_string_put(
        mlx_ptr, win_ptr, WIN_W // 2 - len("Press 1 ro regenerate, 2 for isometric view, 3 for leprechaun, 4 for path, Esc to quit") * 5,  WIN_H // 2 - generated_maze.height * size // 2 - size * 2, 0xFFFFFFFF, "Press 1 ro regenerate, 2 for isometric view, 3 for leprechaun, 4 for path, Esc to quit")
    draw_42(generated_maze)

    app.mlx_loop(mlx_ptr)


def putpath(x, y, size, offset_x, offset_y):
    px = x * size + offset_x + size // 2
    py = y * size + offset_y + size // 2
    draw_cell_path(px, py, size // 2)


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
                putpath(x, y, size, offset_x, offset_y)


def draw_maze_iso(generated_maze: MazeGenerator):
    size = 50
    wall_height = 18
    color = rainbow(random.randint(0, 255), random.randint(0, 255))
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
            x, y, size, cell_variants[cell_value], ox, oy, wall_height, color)
    drawpath_iso(generated_maze, size, ox, oy,
                 wall_height, generated_maze.path)
    draw_42_iso(generated_maze, size, ox, oy, wall_height)
    app.mlx_put_image_to_window(mlx_ptr, win_ptr, img_ptr, 0, 0)
    print("Done !")
    app.mlx_string_put(
        mlx_ptr, win_ptr,
        WIN_W // 2 -
        len("Press 1 flat, 2 iso, 3 leprechaun, 4 path, Esc quit") * 5,
        20,
        0xFFFFFFFF,
        "Press 1 flat, 2 iso, 3 leprechaun, 4 path, Esc quit")
    app.mlx_loop(mlx_ptr)


def leprechaun():
    img, w, h = app.mlx_xpm_file_to_image(mlx_ptr, random.choice(
        ["leprechaun-adam.xpm", "theomartleprehaun.xpm"]))
    app.mlx_put_image_to_window(mlx_ptr, win_ptr, img, 0, 0)
    app.mlx_loop(mlx_ptr)


def destroymaze():
    app.mlx_clear_window(mlx_ptr, win_ptr)
    data_addr[:] = b'\x00' * (WIN_W * WIN_H * BPP)


def putpathblack(x, y, size, offset_x, offset_y):
    px = x * size + offset_x + size // 2
    py = y * size + offset_y + size // 2
    draw_cell_path_black(px, py, size // 2)


def clearpath(generated_maze: MazeGenerator):

    size = 15
    offset_x = 0
    offset_y = 0
    path_coords = generated_maze.path
    print(f"set coordinates: {path_coords}")
    print(f"list coordinates: {generated_maze.path}")
    for y in range(generated_maze.height):
        for x in range(generated_maze.width):
            if (x, y) in path_coords:
                print(f"remooving path cell at ({x}, {y})")
                putpathblack(x, y, size, offset_x, offset_y)


def loop_hook(param):
    return 0
