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
        return ConnectionError

def send_uart_message(message: str):
    try:
        ser = get_uart()
        ser.write((message + '\n').encode('utf-8'))
        print(f"UART sent: {message}")
    except Exception as e:
        print(f"UART send failed: {e}")


def send_effect(effect: int):
    send_uart_message(f"E={effect}")


def send_brightness(percent: int):
    # map 0..100 UI brightness to 0..255 for ESP32
    value_255 = max(0, min(255, int(percent * 255 / 100)))
    send_uart_message(f"B={value_255}")


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
