# ----------------------------------------------------------------
# File: src_ui.py
# Function: Industrial Control UI Layout with 3D Cube and Mapping Table
# Author: Connor Bastian, crb1759@rit.edu
# Date: February 12, 2026
# ----------------------------------------------------------------

# -------------------------------------------------
#               OUTSIDE IMPORTS
# -------------------------------------------------

import serial

# -------------------------------------------------
#               LOCAL IMPORTS
# -------------------------------------------------

import src_params as SP

# -------------------------------------------------
#               USER INTERFACE HELPERS
# -------------------------------------------------

def generate_rainbow_colors(n):
    import colorsys

    colors = []

    for i in range(n):
        hue = i / n
        r, g, b = colorsys.hsv_to_rgb(hue, 1, 1)
        colors.append(f'#{int(r * 255):02x}{int(g * 255):02x}{int(b * 255):02x}')

    return colors
