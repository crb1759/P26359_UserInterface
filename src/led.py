# ----------------------------------------------------------------
# File: led.py
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
    """
    Convert a hex color string into an RGB tuple.

    Args:
        hex_color (str): Color in format '#RRGGBB' or 'RRGGBB'

    Returns:
        tuple[int, int, int]: (red, green, blue) values (0–255)
    """
    # Remove '#' if present
    h = hex_color.lstrip("#")

    # Convert each pair of hex digits into integers
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def hex_to_hue(hex_color: str) -> int:
    """
    Convert a hex color into a WS2812-compatible hue value.

    Uses HSV conversion and scales hue to 0–255 range.

    Args:
        hex_color (str): Input hex color

    Returns:
        int: Hue value (0–255)
    """
    r, g, b = _hex_to_rgb(hex_color)

    # Convert RGB (0–255) → normalized (0–1) for HSV conversion
    h, _s, _v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)

    # Scale hue (0–1) → (0–255)
    return int(h * 255)


def snap_to_ws2812(hex_color: str) -> tuple[str, str]:
    """
    Find the closest WS2812-supported color.

    Uses a perceptual weighted Euclidean distance:
    - Green weighted highest (human eye most sensitive)
    - Red next
    - Blue least

    Args:
        hex_color (str): Input color

    Returns:
        tuple[str, str]: (closest_color_name, closest_hex_value)
    """
    r1, g1, b1 = _hex_to_rgb(hex_color)

    best_name, best_hex, best_dist = "", "", math.inf

    # Compare against predefined WS2812 color set
    for name, ref_hex in PAR.WS281_COLORS.items():
        r2, g2, b2 = _hex_to_rgb(ref_hex)

        # Weighted color distance formula
        dist = math.sqrt(
            2.0 * (r1 - r2) ** 2 +
            4.0 * (g1 - g2) ** 2 +
            3.0 * (b1 - b2) ** 2
        )

        # Track closest match
        if dist < best_dist:
            best_dist = dist
            best_name = name
            best_hex = ref_hex

    return best_name, best_hex


def send_hues_from_hex_list(colors: list[str]) -> None:
    """
    Convert a list of hex colors into hue values and send via UART.

    Limits output to a maximum of 5 colors.

    Args:
        colors (list[str]): List of hex color strings
    """
    # Convert each color → hue (skip empty values)
    hues = [hex_to_hue(c) for c in colors if c]

    if not hues:
        return

    # Limit to maximum of 5 values
    count = min(len(hues), 5)

    # Format as comma-separated string
    hue_csv = ",".join(str(h) for h in hues[:count])

    # Send formatted UART message
    UART.send_uart_message(f"N={count},H={hue_csv}")


# ----------------------------------
#        SENDING EFFECTS
# ----------------------------------

def send_effect(layer: int, effect: int) -> None:
    """
    Send an effect command to a specific LED layer.

    Args:
        layer (int): Layer number (1–3)
        effect (int): Effect code
    """
    # Map layer → UART command key
    key = {1: "E", 2: "E2", 3: "E3"}.get(layer)

    if key:
        UART.send_uart_message(f"{key}={effect}")


def send_brightness(layer: int, percent: int) -> None:
    """
    Send brightness value to a specific layer.

    Converts percentage (0–100%) → 8-bit value (0–255).

    Args:
        layer (int): Layer number (1–3)
        percent (int): Brightness percentage
    """
    # Scale percentage → 0–255 range
    value_255 = max(0, min(255, int(percent * 255 / 100)))

    # Map layer → UART command key
    key = {1: "B", 2: "B2", 3: "B3"}.get(layer)

    if key:
        UART.send_uart_message(f"{key}={value_255}")


def send_override(enabled: bool) -> None:
    """
    Enable or disable override mode.

    Args:
        enabled (bool): True to enable override, False to disable
    """
    UART.send_uart_message("OVR=1" if enabled else "OVR=0")


def send_speed(speed_ms: int) -> None:
    """
    Send effect speed setting.

    Args:
        speed_ms (int): Speed in milliseconds (clamped 1–1000)
    """
    # Clamp speed to safe range
    speed_ms = max(1, min(1000, int(speed_ms)))

    UART.send_uart_message(f"S={speed_ms}")


def send_frequency(freq: float) -> None:
    """
    Send frequency value to hardware.

    Args:
        freq (float): Frequency in Hz (must be non-negative)
    """
    if freq >= 0:
        # Format to 2 decimal places for consistency
        UART.send_uart_message(f"F={freq:.2f}")