"""
Renderer function to draw voxels on the screen buffer.
"""

import numpy as np
from numba import njit


@njit(fastmath=True)
def draw_voxels(out: np.ndarray, out_w: int, out_h: int, pos_x: float, pos_y: float, angle: float,
                horizon: float, elevation: float, scale: float, distance: float,
                height_map: np.ndarray, color_map: np.ndarray) -> int:
    """
    Draw voxels on the screen buffer.
    :param out: Output buffer
    :param out_w: Width of the output buffer
    :param out_h: Height of the output buffer
    :param pos_x: Player position X
    :param pos_y: Player position Y
    :param angle: Player angle
    :param horizon: Player horizon (vertical angle)
    :param elevation: Player elevation (vertical position)
    :param scale: Scale factor for the height map
    :param distance: Maximum distance to draw
    :param height_map: Height map array
    :param color_map: Color map array
    :return: Elevation of the player on the map
    """
    # Clear the buffers
    sky_color = [96, 160, 204]
    out[:] = np.array(sky_color)
    y_buffer = np.full(out_w, out_h)
    fog_color = np.array(sky_color)

    scale_y = 600.0 / out_h
    _horizon = horizon / scale_y
    _scale_height = scale / scale_y
    z = 1.0
    dz = 1.0
    dz_delta = 0.002 * scale_y
    sin_ang = np.sin(angle)
    cos_ang = np.cos(angle)

    # Calculate player position on the map
    icx = int(pos_x - sin_ang) % height_map.shape[0]
    icy = int(pos_y - cos_ang) % height_map.shape[1]

    # Calculate player height on the map
    center_height = int(height_map[icx, icy][0])

    while z < distance:
        # Left and right points on the screen (on the ground)
        lx = -cos_ang * z - sin_ang * z + pos_x
        ly = sin_ang * z - cos_ang * z + pos_y
        rx = cos_ang * z - sin_ang * z + pos_x
        ry = -sin_ang * z - cos_ang * z + pos_y
        # How much position on the map changes per pixel
        dx = (rx - lx) / out_w
        dy = (ry - ly) / out_w
        # Calculate fog level for this row
        fog = int(np.power(z / distance, 3) * 255)

        # Draw the row
        for i in range(0, out_w):
            # Get position on the height map
            ilx = int(lx) % height_map.shape[0]
            ily = int(ly) % height_map.shape[1]

            # Calculate height on the screen for this column
            height_on_screen = int((elevation - height_map[ilx, ily][0]) / z * _scale_height + _horizon)
            if height_on_screen < 0:
                height_on_screen = 0

            # Draw the column if it's higher than the last drawn column (to avoid overdraw and improve performance)
            last_height = y_buffer[i]
            if height_on_screen < last_height:
                color = color_map[ilx, ily]
                for y in range(height_on_screen, last_height):
                    out[i, y][0] = color[0] + ((fog_color[0] - color[0]) * fog >> 8)
                    out[i, y][1] = color[1] + ((fog_color[1] - color[1]) * fog >> 8)
                    out[i, y][2] = color[2] + ((fog_color[2] - color[2]) * fog >> 8)

                y_buffer[i] = height_on_screen

            # Move to the next column
            lx += dx
            ly += dy

        # Move to the next row
        z += dz
        dz += dz_delta

    # Return player height on the map
    return center_height
