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
import time
import math

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


# -------------------------------------------------
#              UART COMMUNICATION
# -------------------------------------------------

_uart = None


def get_uart():
    global _uart

    if _uart is None:

        _uart = serial.Serial(
            port=SP.SERIAL_PORT,
            baudrate=SP.BAUD_RATE,
            timeout=1
        )
        time.sleep(2)

        return _uart

    else:
        print(f"UART Communication Not Initialized")


def send_uart_message(message: str):
    try:
        ser = get_uart()
        ser.write((message + '\n').encode('utf-8'))
        print(f"UART sent: {message}")
    except Exception as e:
        print(f"UART send failed: {e}")


def send_effect(layer: int, effect: int):
    if layer == 1:
        send_uart_message(f'E={effect}')
    elif layer == 2:
        send_uart_message(f'E2={effect}')
    elif layer == 3:
        send_uart_message(f'E3={effect}')


def send_brightness(layer: int, percent: int):
    value_255 = max(0, min(255, int(percent * 255 / 100)))

    if layer == 1:
        send_uart_message(f'B={value_255}')
    elif layer == 2:
        send_uart_message(f'B2={value_255}')
    elif layer == 3:
        send_uart_message(f'B3={value_255}')


def disable_layer(layer: int):
    if layer == 2:
        send_uart_message('X2=1')
    elif layer == 3:
        send_uart_message('X3=1')


def send_override(enabled: bool):
    send_uart_message('OVR=1' if enabled else 'OVR=0')


def hex_to_hue(hex_color: str) -> int:
    # expects '#RRGGBB'
    hex_color = hex_color.lstrip('#')
    if len(hex_color) != 6:
        return 0

    r = int(hex_color[0:2], 16) / 255.0
    g = int(hex_color[2:4], 16) / 255.0
    b = int(hex_color[4:6], 16) / 255.0

    import colorsys
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    return int(h * 255)


def send_hues_from_hex_list(colors: list[str]):
    hues = [hex_to_hue(c) for c in colors if c]
    if not hues:
        return
    hue_csv = ",".join(str(h) for h in hues[:5])
    send_uart_message(f"N={min(len(hues), 5)},H={hue_csv}")


def send_speed(speed_ms: int):
    speed_ms = max(1, min(1000, int(speed_ms)))
    send_uart_message(f"S={speed_ms}")


def send_frequency(freq: float):
    if freq < 0:
        return
    send_uart_message(f"F={freq:.2f}")


def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    """Convert '#RRGGBB' or 'RRGGBB' to an (r, g, b) int tuple."""
    h = hex_color.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


# -------------------------------------------------
# NEAREST-COLOR LOOKUP
# Uses perceptual (weighted Euclidean) distance in RGB space.
# Weights approximate human eye sensitivity: G > R > B.
# -------------------------------------------------

def snap_to_ws2812(hex_color: str) -> tuple[str, str]:
    """
    Given any arbitrary hex color, return the closest WS2812
    obtainable color as a (name, hex) tuple.

    Example
    -------
    >>> snap_to_ws2812("#FE0102")
    ('Red', '#FF0000')
    """
    r1, g1, b1 = _hex_to_rgb(hex_color)

    best_name = ""
    best_hex = ""
    best_dist = math.inf

    for name, ref_hex in SP.WS281_COLORS.items():
        r2, g2, b2 = _hex_to_rgb(ref_hex)

        # Weighted Euclidean distance (perceptual approximation)
        dist = math.sqrt(
            2.0 * (r1 - r2) ** 2 +
            4.0 * (g1 - g2) ** 2 +
            3.0 * (b1 - b2) ** 2
        )

        if dist < best_dist:
            best_dist = dist
            best_name = name
            best_hex = ref_hex

    return best_name, best_hex
