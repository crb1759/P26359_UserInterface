# ----------------------------------------------------------------
# File: uart.py
# Function: LED Functions for UI Interface
# Author: Connor Bastian
# Date: February 12, 2026
# ----------------------------------------------------------------

# Local Imports
import uart as UART
import params as PAR

# Outside Imports
import math
import colorsys


def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    """Convert '#RRGGBB' or 'RRGGBB' to an (r, g, b) int tuple."""
    h = hex_color.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def hex_to_hue(hex_color: str) -> int:
    """Convert a hex color to a WS2812-compatible hue value (0–255)."""
    r, g, b = _hex_to_rgb(hex_color)
    h, _s, _v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
    return int(h * 255)


def snap_to_ws2812(hex_color: str) -> tuple[str, str]:
    """
    Return the closest WS2812-obtainable color as (name, hex).
    Uses perceptual weighted Euclidean distance (G > R > B sensitivity).
    """
    r1, g1, b1 = _hex_to_rgb(hex_color)
    best_name, best_hex, best_dist = "", "", math.inf

    for name, ref_hex in PAR.WS281_COLORS.items():
        r2, g2, b2 = _hex_to_rgb(ref_hex)
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

def send_hues_from_hex_list(colors: list[str]) -> None:
    """Convert up to 5 hex colors to hue values and send them."""
    hues = [hex_to_hue(c) for c in colors if c]
    if not hues:
        return
    count = min(len(hues), 5)
    hue_csv = ",".join(str(h) for h in hues[:count])
    UART.send_uart_message(f"N={count},H={hue_csv}")

# ----------------------------------
#        SENDING EFFECTS
# ----------------------------------

def send_effect(layer: int, effect: int) -> None:
    """Send an effect code to the given layer (1–3)."""
    key = {1: "E", 2: "E2", 3: "E3"}.get(layer)
    if key:
        UART.send_uart_message(f"{key}={effect}")


def send_brightness(layer: int, percent: int) -> None:
    """Send a brightness value (0–100%) scaled to 0–255."""
    value_255 = max(0, min(255, int(percent * 255 / 100)))
    key = {1: "B", 2: "B2", 3: "B3"}.get(layer)
    if key:
        UART.send_uart_message(f"{key}={value_255}")


def send_override(enabled: bool) -> None:
    UART.send_uart_message("OVR=1" if enabled else "OVR=0")


def send_speed(speed_ms: int) -> None:
    speed_ms = max(1, min(1000, int(speed_ms)))
    UART.send_uart_message(f"S={speed_ms}")


def send_frequency(freq: float) -> None:
    if freq >= 0:
        UART.send_uart_message(f"F={freq:.2f}")
