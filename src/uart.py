# ----------------------------------------------------------------
# File: uart.py
# Function: UART Functions for UI Interface
# Author: Connor Bastian
# Date: February 12, 2026
# ----------------------------------------------------------------

import params as PAR
import led as LED
import serial
import time

# Shared UART instance (lazy initialized)
_uart: serial.Serial | None = None

# Tracks last override state to avoid redundant UART messages
_ovr_state = False


def get_uart() -> serial.Serial:
    """
    Get or initialize the shared UART (Serial) connection.

    Uses lazy initialization so the port is only opened when needed.

    Returns:
        serial.Serial: Active serial connection object
    """
    global _uart

    if _uart is None:
        # Initialize serial connection using parameters
        _uart = serial.Serial(
            port=PAR.SERIAL_PORT,
            baudrate=PAR.BAUD_RATE,
            timeout=1,
        )

        # Allow time for device (e.g., microcontroller) to reset
        time.sleep(2)

    return _uart


def send_uart_message(message: str) -> bool:
    """
    Send a raw UART message string.

    Automatically appends newline and encodes as UTF-8.

    Args:
        message (str): Message to send

    Returns:
        bool: True if successful, False if error occurred
    """
    try:
        ser = get_uart()

        # Append newline to match expected protocol framing
        ser.write((message + "\n").encode("utf-8"))

        print(f"UART sent: {message}")
        return True

    except Exception as e:
        print(f"UART send failed: {e}")
        return False


def send(override: bool | None = None, **kwargs) -> bool:
    """
    High-level send function that builds and transmits a UART message.

    Args:
        override (bool | None): Optional override state
        **kwargs: Message fields (effect, colors, brightness, etc.)

    Returns:
        bool: True if send succeeded, False otherwise
    """
    # Build formatted UART message string
    msg = build_message(**kwargs, override=override)

    # Prevent sending empty messages
    if not msg:
        print("[WARN] Empty UART message — nothing sent")
        return False

    success = send_uart_message(msg)

    if not success:
        print(f"[WARN] Tried to send message but UART failed: {msg}")

    return success


def build_message(
    effect: int | None = None,
    colors: list[str] | None = None,
    brightness: int | None = None,
    frequency: float | None = None,
    speed: int | None = None,
    override: bool | None = None,
) -> str:
    """
    Construct a UART message string following protocol format.

    Example:
        E=5,N=3,H=20,80,140,B=180,F=440.00,S=25

    Only fields that are not None are included.

    Args:
        effect (int): Effect ID
        colors (list[str]): List of hex colors
        brightness (int): Brightness (0–255)
        frequency (float): Frequency value
        speed (int): Effect speed
        override (bool): Override state

    Returns:
        str: Comma-separated UART message string
    """
    global _ovr_state

    parts = []

    # Effect command
    if effect is not None:
        parts.append(f"E={int(effect)}")

    # Color handling (convert hex → hue values)
    if colors:
        # Convert each color to WS2812 hue
        hues = [LED.hex_to_hue(c) for c in colors if c]

        # Limit number of colors sent
        count = min(len(hues), 5)

        # Convert list to CSV string
        hue_csv = ",".join(str(h) for h in hues[:count])

        # N = number of colors, H = hue values
        parts.append(f"N={count}")
        parts.append(f"H={hue_csv}")

    # Brightness (clamped to 0–255)
    if brightness is not None:
        parts.append(f"B={max(0, min(255, int(brightness)))}")

    # Frequency formatted to 2 decimal places
    if frequency is not None:
        parts.append(f"F={frequency:.2f}")

    # Speed clamped to safe range
    if speed is not None:
        parts.append(f"S={max(1, min(999, int(speed)))}")

    # Only send override command if state changes
    if override is not None and override != _ovr_state:
        parts.append(f"OVR={1 if override else 0}")
        _ovr_state = override

    # Join all parts into final message string
    return ",".join(parts)