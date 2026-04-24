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

_uart: serial.Serial | None = None

_ovr_state = False

def get_uart() -> serial.Serial:
    """
    Return the shared Serial instance, initializing it on first call.
    Always returns the object — never None.
    """
    global _uart
    if _uart is None:
        _uart = serial.Serial(
            port=PAR.SERIAL_PORT,
            baudrate=PAR.BAUD_RATE,
            timeout=1,
        )
        time.sleep(2)
    return _uart


def send_uart_message(message: str) -> bool:

    try:
        ser = get_uart()
        ser.write((message + "\n").encode("utf-8"))
        print(f"UART sent: {message}")
        return True
    except Exception as e:
        print(f"UART send failed: {e}")
        return False

def send(override: bool | None = None, **kwargs) -> bool:
    """
    Build and send a UART message in one step.
    Returns True on success, False on failure.
    """
    msg = build_message(**kwargs, override=override)

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
    Build a UART message in the protocol format:
        E=5,N=3,H=20,80,140,B=180,F=440.00,S=25
    Only fields that are not None are included.
    """
    global _ovr_state

    parts = []

    if effect is not None:
        parts.append(f"E={int(effect)}")

    if colors:
        hues = [LED.hex_to_hue(c) for c in colors if c]
        count = min(len(hues), 5)
        hue_csv = ",".join(str(h) for h in hues[:count])
        parts.append(f"N={count}")
        parts.append(f"H={hue_csv}")

    if brightness is not None:
        parts.append(f"B={max(0, min(255, int(brightness)))}")

    if frequency is not None:
        parts.append(f"F={frequency:.2f}")

    if speed is not None:
        parts.append(f"S={max(1, min(999, int(speed)))}")

    if override is not None and override != _ovr_state:
        parts.append(f"OVR={1 if override else 0}")
        _ovr_state = override

    return ",".join(parts)