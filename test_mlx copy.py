from mlx import Mlx
import os
import random
import math
app = Mlx()
mlx_ptr = app.mlx_init()
win_ptr = app.mlx_new_window(mlx_ptr, 3840, 2160, "A-Mazing")


def close_win(param):

    os._exit(0)


def key_hook(keycode, param):
    if keycode == 65307:
        os._exit(0)


app.mlx_hook(win_ptr, 33, 0, close_win, None)
app.mlx_key_hook(win_ptr, key_hook, None)


cell_variants = {
    0:  {"N": False, "S": False, "E": False, "W": False},
    1:  {"N": False, "S": False, "E": False, "W": True},
    2:  {"N": False, "S": False, "E": True,  "W": False},
    3:  {"N": False, "S": False, "E": True,  "W": True},

    4:  {"N": False, "S": True,  "E": False, "W": False},
    5:  {"N": False, "S": True,  "E": False, "W": True},
    6:  {"N": False, "S": True,  "E": True,  "W": False},
    7:  {"N": False, "S": True,  "E": True,  "W": True},

    8:  {"N": True,  "S": False, "E": False, "W": False},
    9:  {"N": True,  "S": False, "E": False, "W": True},
    10: {"N": True,  "S": False, "E": True,  "W": False},
    11: {"N": True,  "S": False, "E": True,  "W": True},

    12: {"N": True,  "S": True,  "E": False, "W": False},
    13: {"N": True,  "S": True,  "E": False, "W": True},
    14: {"N": True,  "S": True,  "E": True,  "W": False},
    15: {"N": True,  "S": True,  "E": True,  "W": True},
}


def to_iso(gx, gy, hw, hh, origin_x, origin_y):
    """Convert grid coords to isometric screen coords."""
    sx = origin_x + (gx - gy) * hw
    sy = origin_y + (gx + gy) * hh
    return (sx, sy)


def blend_color(color, t):
    """
    t = 0.0 → couleur pleine (bas du mur)
    t = 1.0 → couleur sombre (haut du mur)
    """
    a = (color >> 24) & 0xFF
    r = (color >> 16) & 0xFF
    g = (color >> 8) & 0xFF
    b = (color) & 0xFF

    dark = 0.25  # le haut du mur sera à 25% de la luminosité
    factor = 0.23 + t * (1.0 - dark)

    r = int(r * factor)
    g = int(g * factor)
    b = int(b * factor)
    return (a << 24) | (r << 16) | (g << 8) | b


def draw_wall_face(app, mlx_ptr, win_ptr, p0, p1, wall_height, color):
    x0, y0 = p0
    x1, y1 = p1
    x2, y2 = x1, y1 - wall_height
    x3, y3 = x0, y0 - wall_height

    y_min = int(min(y0, y1, y2, y3))
    y_max = int(max(y0, y1, y2, y3))

    def x_on_segment(xa, ya, xb, yb, y):
        if ya == yb:
            return None
        t = (y - ya) / (yb - ya)
        if 0 <= t <= 1:
            return xa + t * (xb - xa)
        return None

    def y_on_segment(xa, ya, xb, yb, x):
        if xa == xb:
            return None
        t = (x - xa) / (xb - xa)
        if 0 <= t <= 1:
            return ya + t * (yb - ya)
        return None

    edges = [(x0, y0, x3, y3), (x3, y3, x2, y2),
             (x2, y2, x1, y1), (x1, y1, x0, y0)]
    bottom_edges = [(x0, y0, x1, y1)]
    top_edges = [(x3, y3, x2, y2)]

    for y in range(y_min, y_max + 1):
        xs = []
        for (xa, ya, xb, yb) in edges:
            x = x_on_segment(xa, ya, xb, yb, y)
            if x is not None:
                xs.append(x)
        if len(xs) >= 2:
            x_left = int(min(xs))
            x_right = int(max(xs))

            for x in range(x_left, x_right + 1):
                y_base = next(
                    (y_on_segment(xa, ya, xb, yb, x)
                     for (xa, ya, xb, yb) in bottom_edges
                     if y_on_segment(xa, ya, xb, yb, x) is not None),
                    None
                )
                y_top = next(
                    (y_on_segment(xa, ya, xb, yb, x)
                     for (xa, ya, xb, yb) in top_edges
                     if y_on_segment(xa, ya, xb, yb, x) is not None),
                    None
                )

                if y_base is None or y_top is None or y_base == y_top:
                    t = 0.5
                else:
                    t = (y_base - y) / (y_base - y_top)
                    t = max(0.0, min(1.0, t))

                app.mlx_pixel_put(mlx_ptr, win_ptr, x, y,
                                  blend_color(color, t))


def rainbow(x, y):
    scale = 0.05
    t = x + y
    r = int(127 + 127 * math.sin(scale * t))
    g = int(127 + 127 * math.sin(scale * t + 2))
    b = int(127 + 127 * math.sin(scale * t + 4))
    return (0xFF << 24) | (r << 16) | (g << 8) | b


def draw_cell(x, y, size, cell,
              origin_x=1800, origin_y=200, wall_height=20):
    """
    Draw a maze cell in isometric projection.
    origin_x/y is the screen-space origin of grid (0,0).
    wall_height controls how tall the walls appear.
    """
    hw = size // 2   # half diamond width
    hh = size // 4   # half diamond height  (2:1 iso ratio)

    # The 4 corners of this cell in grid space
    # (x,y), (x+1,y), (x+1,y+1), (x,y+1)
    corners = [
        to_iso(x,   y,   hw, hh, origin_x, origin_y),  # top
        to_iso(x+1, y,   hw, hh, origin_x, origin_y),  # right
        to_iso(x+1, y+1, hw, hh, origin_x, origin_y),  # bottom
        to_iso(x,   y+1, hw, hh, origin_x, origin_y),  # left
    ]
    TL, TR, BR, BL = corners
    color = rainbow(x, y)

    # North wall: top-left face (TL → TR)
    if cell["N"]:
        draw_wall_face(app, mlx_ptr, win_ptr, TL, TR, wall_height, color)

    # South wall: bottom face (BL → BR)
    if cell["S"]:
        draw_wall_face(app, mlx_ptr, win_ptr, BL, BR, wall_height, color)

    # West wall: top-right face (TL → BL)
    if cell["W"]:
        draw_wall_face(app, mlx_ptr, win_ptr, TL, BL, wall_height, color)

    # East wall: right face (TR → BR)
    if cell["E"]:
        draw_wall_face(app, mlx_ptr, win_ptr, TR, BR, wall_height, color)


maze = [[cell_variants[random.randint(0, 15)]
         for _ in range(20)] for _ in range(20)]


def loop_hook(param):
    size = 100
    for y in range(20):
        for x in range(20):
            draw_cell(x, y, size, maze[y][x])

    return 0


app.mlx_loop_hook(mlx_ptr, loop_hook, None)

color = 0xFFFF0000

# for i in range(30):
#     for j in range(30):
#         app.mlx_pixel_put(mlx_ptr, win_ptr, i, j, color)

# img, w, h = app.mlx_xpm_file_to_image(mlx_ptr, "leprechaun-adam.xpm")
# app.mlx_put_image_to_window(mlx_ptr, win_ptr, img, 0, 0)

app.mlx_loop(mlx_ptr)
