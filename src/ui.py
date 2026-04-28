# ----------------------------------------------------------------
# File: ui.py
# Function: Industrial Control UI Layout
# Author: Connor Bastian
# Date: February 12, 2026
# ----------------------------------------------------------------

from nicegui import ui
from collections import deque

import params as PAR
import uart as UART
import led as LED

# -------------------------------------------------
# GLOBAL DATA
# -------------------------------------------------

# Ordered rainbow color keys used for band color assignment
_rainbow_keys = ["Red", "Orange", "Yellow", "Green", "Cyan", "Blue", "Violet", "Magenta"]

# Convert color names into actual WS2812-compatible hex values
_rainbow_palette = [PAR.WS281_COLORS[k] for k in _rainbow_keys]


def _pick_rainbow(i, n):
    """
    Selects a color from the rainbow palette based on index.

    Args:
        i (int): Current index
        n (int): Total number of bands

    Returns:
        str: Hex color value evenly spaced across palette
    """
    # Scale index proportionally across palette size
    idx = round(i * (len(_rainbow_palette) - 1) / max(n - 1, 1))
    return _rainbow_palette[idx]


# Initialize frequency bands with evenly spaced ranges and colors
bands = [
    {
        "freq_min": int(i * PAR.BAND_STEP),
        "freq_max": int((i + 1) * PAR.BAND_STEP),
        "color": _pick_rainbow(i, PAR.NUM_BANDS),
    }
    for i in range(PAR.NUM_BANDS)
]

# Convert initial brightness from percentage → 0–255 scale
brightness = max(0, min(255, int(PAR.INIT_CUBE_BRIGHTNESS_PERCENT * 255 / 100)))

# Tracks if any frequency bands overlap
_overlap_error = False

# Currently active lighting effect
_active_effect = None

# FIFO queue of selected colors for effects
_selected_colors = deque(maxlen=PAR.EFFECT_COLOR_LIMIT)

# Rules defining behavior for each lighting effect
EFFECT_RULES = {
    PAR.FLASH_CMD:  {"min": 1, "max": 1, "auto_start": False},
    PAR.SMOOTH_CMD: {"min": 1, "max": 1, "auto_start": True},   # default on boot
    PAR.STROBE_CMD: {"min": 1, "max": PAR.EFFECT_COLOR_LIMIT, "auto_start": False},
    PAR.FADE_CMD:   {"min": 1, "max": PAR.EFFECT_COLOR_LIMIT, "auto_start": False},
}

# -------------------------------------------------
# OVERLAP CHECK
# -------------------------------------------------

def check_overlap() -> bool:
    """
    Checks if any frequency bands overlap.

    Updates the UI error label and blocks UART transmission if overlap exists.

    Returns:
        bool: True if overlap detected, False otherwise
    """
    global _overlap_error
    active_ranges = []

    # Collect valid frequency ranges
    for band in bands:
        min_f = band["freq_min"]
        max_f = band["freq_max"]

        # Skip uninitialized or zeroed bands
        if min_f is None or max_f is None:
            continue
        if min_f == 0 and max_f == 0:
            continue

        active_ranges.append((min_f, max_f))

    # Compare each pair of ranges for overlap
    for i in range(len(active_ranges)):
        for j in range(i + 1, len(active_ranges)):
            a_min, a_max = active_ranges[i]
            b_min, b_max = active_ranges[j]

            # Overlap condition
            if a_min < b_max and b_min < a_max:
                _overlap_error = True
                error_label.set_text("⚠ Frequency Ranges Overlap! ⚠")
                error_label.classes(remove="hidden")
                return True

    # No overlap detected → clear error state
    _overlap_error = False
    error_label.set_text("")
    error_label.classes(add="hidden")
    return False


def _can_send() -> bool:
    """Returns True if UART communication is allowed."""
    return not _overlap_error


def send_uart(**kwargs):
    """
    Wrapper for UART send function.

    Args:
        **kwargs: Parameters passed directly to UART.send()
    """
    UART.send(**kwargs)

# -------------------------------------------------
# EVENT HANDLERS
# -------------------------------------------------

def _on_freq_change(e, idx):
    """
    Handles frequency slider updates for a band.

    Updates band range, UI label, checks overlap,
    and sends center frequency to hardware.

    Args:
        e: UI event containing slider values
        idx (int): Band index
    """
    lo = round(e.value["min"])
    hi = round(e.value["max"])

    # Update internal band data
    bands[idx]["freq_min"] = lo
    bands[idx]["freq_max"] = hi

    # Update displayed label
    hz_labels[idx].set_text(f"{lo}–{hi} Hz")

    # Prevent sending if overlap detected
    if check_overlap():
        return

    # Calculate center frequency
    center = (lo + hi) / 2.0

    send_uart(
        frequency=center,
        colors=[bands[idx]["color"]],
        override=False
    )


def _on_band_color_change(e, idx, sw):
    """
    Handles color picker changes for a frequency band.

    Snaps color to valid WS2812 value and updates UI + hardware.

    Args:
        e: UI event containing selected color
        idx (int): Band index
        sw: UI swatch element to update appearance
    """
    raw_hex = str(e.value)

    # Ignore invalid color values
    if not raw_hex.startswith("#"):
        return

    # Snap to closest WS2812-compatible color
    _name, snapped = LED.snap_to_ws2812(raw_hex)

    bands[idx]["color"] = snapped

    # Update swatch styling
    sw.style(
        f"width:28px; height:28px; border-radius:6px; "
        f"background-color:{snapped}; "
        f"border:1px solid #555; flex-shrink:0; cursor:pointer;"
    )

    if not _can_send():
        return

    send_uart(colors=[snapped], override=False)


def _arm_effect(effect_id, auto=False):
    """
    Activates a lighting effect and resets color queue.

    Args:
        effect_id: Effect command identifier
        auto (bool): If True, auto-start effect with default color
    """
    global _active_effect, _selected_colors

    rules = EFFECT_RULES[effect_id]

    _active_effect = effect_id

    # Reset FIFO queue with new max size
    _selected_colors = deque(maxlen=rules["max"])
    _selected_colors.clear()

    # Auto-start effect with first band color if required
    if auto and rules["min"] == 1:
        default_color = bands[0]["color"]
        _, snapped = LED.snap_to_ws2812(default_color)

        _selected_colors.append(snapped)

        send_uart(
            effect=_active_effect,
            colors=list(_selected_colors),
            override=True
        )


def _on_manual_color(col):
    """
    Handles manual color button presses.

    Adds color to FIFO queue and triggers active effect.

    Args:
        col (str): Selected color hex value
    """
    global _selected_colors, _active_effect

    if not col.startswith("#"):
        return

    _, snapped = LED.snap_to_ws2812(col)

    # Ensure an effect is active
    if _active_effect is None:
        _arm_effect(PAR.SMOOTH_CMD)

    rules = EFFECT_RULES[_active_effect]

    # Move existing color to end (refresh behavior)
    if snapped in _selected_colors:
        _selected_colors.remove(snapped)

    _selected_colors.append(snapped)

    # Send only when minimum requirement met
    if len(_selected_colors) >= rules["min"]:
        send_uart(
            effect=_active_effect,
            colors=list(_selected_colors),
            override=True
        )


def update_brightness(value):
    """
    Updates brightness level and sends to hardware.

    Args:
        value (float): Brightness percentage (0–100)
    """
    global brightness

    brightness_label.set_text(f"Brightness: {int(value)}%")

    # Convert to 0–255 scale
    brightness = max(0, min(255, int(value * 255 / 100)))

    send_uart(brightness=brightness)


def start_flash():
    """Activate flash effect."""
    _arm_effect(PAR.FLASH_CMD)


def start_strobe():
    """Activate strobe effect."""
    _arm_effect(PAR.STROBE_CMD)


def start_fade():
    """Activate fade effect."""
    _arm_effect(PAR.FADE_CMD)


def start_smooth():
    """Activate smooth effect."""
    _arm_effect(PAR.SMOOTH_CMD)


def stop_effects():
    """
    Stops active effects and restores band-based color control.
    """
    global _active_effect, _selected_colors

    _active_effect = None
    _selected_colors.clear()

    # Restore all band colors
    all_colors = [band["color"] for band in bands]

    send_uart(colors=all_colors, override=False)


# -------------------------------------------------
# STYLING
# -------------------------------------------------

ui.add_head_html("""
<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@700&display=swap" rel="stylesheet">
<style>
html, body {
    margin: 0;
    padding: 0;
    overflow: hidden;
    width: 100vw;
    height: 100vh;
    background-color: #1E1E1E;
}

.infinity-title {
    font-size: 2rem;
    font-weight: 700;
    font-family: "Orbitron", "Segoe UI", sans-serif;
    animation: colorFlicker 4s infinite linear;
    -webkit-text-stroke: 1.5px white;
}

@keyframes colorFlicker {
    0%   { color: #ff0000; }
    33%  { color: #00ff00; }
    66%  { color: #0000ff; }
    100% { color: #ff0000; }
}

*, *::before, *::after {
    box-sizing: border-box;
}
</style>
""")

# -------------------------------------------------
# MAIN LAYOUT
# -------------------------------------------------

hz_labels = []

# Main container with fixed resolution
with ui.column().classes("w-[1024px] h-[600px] mx-auto gap-2"):

    # Animated title
    ui.label("∞ Infinity Cube ∞").classes("infinity-title w-full text-center")

    ui.separator()

    # Two-column layout
    with ui.row().classes("w-full flex-1 no-wrap gap-4"):

        # LEFT — Frequency Bands
        with ui.column().classes("w-1/2 h-full gap-2 items-center"):

            ui.label("Frequency Band Control").classes(
                "text-lg font-semibold text-gray-200 text-center"
            )

            for i in range(PAR.NUM_BANDS):
                band = bands[i]

                with ui.row().classes("items-center gap-3 w-full"):

                    ui.label(f"Band {i + 1}").classes("text-xs text-gray-400 w-16")

                    # Dual-handle slider for frequency range
                    slider = ui.range(
                        min=0,
                        max=PAR.MAX_FREQ,
                        value={"min": band["freq_min"], "max": band["freq_max"]},
                    ).classes("flex-1")

                    # Label displaying current range
                    lbl = ui.label(
                        f"{int(band['freq_min'])}–{int(band['freq_max'])} Hz"
                    ).classes("text-xs text-gray-400 w-28 text-right")

                    hz_labels.append(lbl)

                    # Bind slider change event
                    slider.on_value_change(lambda e, idx=i: _on_freq_change(e, idx))

                    # Hidden color picker (triggered via swatch click)
                    color_input = ui.color_input(value=band["color"]).props("hide-bottom-space")
                    color_input.classes("w-0 overflow-hidden p-0 m-0")

                    # Visible color swatch
                    swatch = ui.element("div").style(
                        f"width:28px; height:28px; border-radius:6px; "
                        f"background-color:{band['color']}; "
                        f"border:1px solid #555; flex-shrink:0; cursor:pointer;"
                    )

                    # Handle color change
                    color_input.on(
                        "change",
                        lambda e, idx=i, sw=swatch: _on_band_color_change(e, idx, sw)
                    )

                    # Assign unique ID to hidden input
                    input_el_id = f"ci_{i}"
                    color_input.props(f'id="{input_el_id}"')

                    # Clicking swatch triggers hidden color picker via JS
                    swatch.on("click", lambda _, eid=input_el_id: ui.run_javascript(f"""
                        var el = document.querySelector('#{eid} .q-color-picker-trigger');
                        if (el) el.click();
                    """))

        # RIGHT — Manual Controls
        with ui.column().classes("w-1/2 h-full gap-2 items-center"):

            ui.label("Manual Color Control").classes(
                "text-lg font-semibold text-gray-200 text-center"
            )

            # Predefined selectable colors
            manual_colors = [
                PAR.WS281_COLORS["Crimson"], PAR.WS281_COLORS["Orange"],
                PAR.WS281_COLORS["Yellow"], PAR.WS281_COLORS["Green"],
                PAR.WS281_COLORS["Cyan"], PAR.WS281_COLORS["Dodger Blue"],
                PAR.WS281_COLORS["Blue"], PAR.WS281_COLORS["Violet"],
                PAR.WS281_COLORS["Magenta"], PAR.WS281_COLORS["Hot Pink"],
                PAR.WS281_COLORS["White"], PAR.WS281_COLORS["Warm White"],
                PAR.WS281_COLORS["Periwinkle"], PAR.WS281_COLORS["Amber"],
                PAR.WS281_COLORS["Mint"], PAR.WS281_COLORS["Raspberry"],
            ]

            # Grid of color buttons
            with ui.grid(columns=4).classes("gap-x-12 gap-y-10"):
                for color in manual_colors:
                    ui.button("") \
                        .props("flat") \
                        .classes("w-12 h-12 rounded-full border-2 border-gray-700 !bg-transparent") \
                        .style(f"background-color: {color} !important; box-shadow: 0 0 10px {color};") \
                        .on("click", lambda e, c=color: _on_manual_color(c))

            ui.separator().classes("w-full")

            # Effect control buttons
            with ui.row().classes("gap-4 flex-wrap justify-center"):
                ui.button("Flash").on("click", lambda: start_flash())
                ui.button("Strobe").on("click", lambda: start_strobe())
                ui.button("Fade").on("click", lambda: start_fade())
                ui.button("Smooth").on("click", lambda: start_smooth())
                ui.button("Stop").on("click", lambda: stop_effects())

    # -------------------------------------------------
    # ERROR + BRIGHTNESS
    # -------------------------------------------------

    # Error label for overlap detection
    error_label = ui.label("").classes("text-red-500 text-center hidden")

    ui.separator()

    # Brightness display
    brightness_label = ui.label(f"Brightness: {PAR.INIT_CUBE_BRIGHTNESS_PERCENT}%").classes(
        "text-sm text-gray-300 text-center"
    )

    # Brightness slider
    ui.slider(min=0, max=100, value=PAR.INIT_CUBE_BRIGHTNESS_PERCENT).classes("w-full").on_value_change(
        lambda e: update_brightness(e.value)
    )

# Start UI server
ui.run()