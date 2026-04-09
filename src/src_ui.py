# ----------------------------------------------------------------
# File: src_ui.py
# Function: Industrial Control UI Layout
# Author: Connor Bastian
# Date: February 12, 2026
# ----------------------------------------------------------------

from nicegui import ui

import src_params as SP
import src_func as SF

import webcolors

# -------------------------------------------------
# GLOBAL DATA
# -------------------------------------------------

rainbow = SF.generate_rainbow_colors(SP.NUM_BANDS)

bands = [
    {
        "min_freq": i * SP.BAND_STEP,
        "max_freq": (i + 1) * SP.BAND_STEP,
        "intensity": 50,
        "color": rainbow[i],
    }
    for i in range(SP.NUM_BANDS)
]

band_step = SP.MAX_FREQ / SP.NUM_BANDS

color_buttons = []
range_sliders = []

manual_color: str = SP.WS281_COLORS["Teal"]


# -------------------------------------------------
# PAGE SWITCHING
# -------------------------------------------------

def show_frequency():
    frequency_page.classes(remove="hidden")
    manual_page.classes(add="hidden")


def show_manual():
    frequency_page.classes(add="hidden")
    manual_page.classes(remove="hidden")


# -------------------------------------------------
# LOGIC FUNCTIONS
# -------------------------------------------------


def check_overlap():
    active_ranges = []

    for band in bands:
        min_f = band["min_freq"]
        max_f = band["max_freq"]

        if min_f is None or max_f is None:
            continue

        if min_f == 0 and max_f == 0:
            continue

        active_ranges.append((min_f, max_f))

    for i in range(len(active_ranges)):
        for j in range(i + 1, len(active_ranges)):
            a_min, a_max = active_ranges[i]
            b_min, b_max = active_ranges[j]

            if a_min < b_max and b_min < a_max:
                error_label.set_text("⚠ Frequency Ranges Overlap! ⚠")
                error_label.classes(remove="hidden")
                return

    error_label.set_text("")
    error_label.classes(add="hidden")


def update_cube_colors():
    faces = ["front", "back", "right", "left", "top", "bottom"]

    for i in range(min(6, len(bands))):
        color = bands[i]["color"]

        ui.run_javascript(f"""
            const face = document.getElementById('cube_{faces[i]}');
            if (face) {{
                face.style.background = '{color}';
                face.style.border = '2px solid {color}';
                face.style.boxShadow = '0 0 20px {color}';
            }}
        """)

    colors = [band["color"] for band in bands]
    ui.run_javascript(f"""
        if (typeof window.freqPreviewInterval !== 'undefined') {{
            window.freqPreviewColors = {str(colors)};
        }}
    """)


def _start_frequency_preview():

    colors = [band["color"] for band in bands]
    colors_js = str(colors)

    ui.run_javascript(f"""
        window.freqPreviewColors = {colors_js};
        window.freqPreviewIndex  = 0;
 
        clearInterval(window.freqPreviewInterval);
 
        function _applyFreqColor(hex) {{
            const border = hex;
            const fill   = hex + '33';
            document.querySelectorAll('.face').forEach(face => {{
                face.style.border    = '2px solid ' + border;
                face.style.boxShadow = '0 0 20px '  + border;
                face.style.background = fill;
            }});
        }}
 
        // Cross-fade by incrementing hue smoothly toward target
        // We swap color every 1.2 s with a CSS transition on the face
        document.querySelectorAll('.face').forEach(face => {{
            face.style.transition = 'border-color 0.8s ease, box-shadow 0.8s ease, background 0.8s ease';
        }});
 
        _applyFreqColor(window.freqPreviewColors[0]);
 
        window.freqPreviewInterval = setInterval(() => {{
            window.freqPreviewIndex = (window.freqPreviewIndex + 1) % window.freqPreviewColors.length;
            _applyFreqColor(window.freqPreviewColors[window.freqPreviewIndex]);
        }}, 1200);
    """)


def stop_frequency_preview():
    ui.run_javascript("""
        clearInterval(window.freqPreviewInterval);
        document.querySelectorAll('.face').forEach(face => {
            face.style.transition = '';
        });
    """)


# -------------------------------------------------
#               LED CONTROL FUNCTIONS
# -------------------------------------------------


def update_color(index, value):
    bands[index]["color"] = value
    update_cube_colors()

    # Send Command(s) to ESP32
    selected = [band["color"] for band in bands[:5]]
    SF.send_hues_from_hex_list(selected)


def update_brightness(value):
    brightness_label.set_text(f"Brightness: {value}%")
    brightness_factor = value / 100

    # Send Command(s) to ESP32
    SF.send_brightness(int(value))

    # Update Cube Rendering
    ui.run_javascript(f"""
        const faces = document.querySelectorAll('.face');
        faces.forEach(face => {{
            face.style.filter = "brightness({brightness_factor})";
        }});
    """)


def start_flash():
    # Send Command(s) to ESP32
    SF.send_effect(SP.FLASH_CMD)
    SF.send_speed(250)

    # Update Cube Rendering
    ui.run_javascript("""
        window.ledInterval && clearInterval(window.ledInterval);

        const colors = ['red','green','blue','yellow','purple','cyan','white'];
        let i = 0;

        window.ledInterval = setInterval(() => {
            const faces = document.querySelectorAll('.face');
            faces.forEach(face => {
                face.style.borderColor = colors[i];
                face.style.boxShadow = `0 0 20px ${colors[i]}`;
            });
            i = (i + 1) % colors.length;
        }, 200);
    """)


def start_strobe():
    # Send Command(s) to ESP32
    SF.send_effect(SP.STROBE_CMD)
    SF.send_speed(100)

    # Update Cube Rendering
    ui.run_javascript("""
        window.ledInterval && clearInterval(window.ledInterval);

        let on = true;

        window.ledInterval = setInterval(() => {
            const faces = document.querySelectorAll('.face');
            faces.forEach(face => {
                face.style.opacity = on ? 1 : 0.1;
            });
            on = !on;
        }, 100);
    """)


def start_fade():
    # Send Command(s) to ESP32
    SF.send_effect(SP.FADE_CMD)
    SF.send_speed(30)

    # Update Cube Rendering
    ui.run_javascript("""
        window.ledInterval && clearInterval(window.ledInterval);

        let hue = 0;

        window.ledInterval = setInterval(() => {
            const color = `hsl(${hue}, 100%, 50%)`;
            const faces = document.querySelectorAll('.face');

            faces.forEach(face => {
                face.style.borderColor = color;
                face.style.boxShadow = `0 0 20px ${color}`;
            });

            hue = (hue + 1) % 360;
        }, 30);
    """)


def start_smooth():
    # Send Command(s) to ESP32
    SF.send_effect(SP.SMOOTH_CMD)
    SF.send_speed(18)

    # Update Cube Rendering
    ui.run_javascript("""
        window.ledInterval && clearInterval(window.ledInterval);

        let hue = 0;

        window.ledInterval = setInterval(() => {
            const color = `hsl(${hue}, 100%, 50%)`;
            const faces = document.querySelectorAll('.face');

            faces.forEach(face => {
                face.style.borderColor = color;
                face.style.boxShadow = `0 0 30px ${color}`;
            });

            hue = (hue + 0.3) % 360;
        }, 30);
    """)


def start_snake():

    color = manual_color

    r = int(color[1:3], 16)
    g = int(color[3:5], 16)
    b = int(color[5:7], 16)

    # Update Cube Rendering
    ui.run_javascript(f"""
        window.ledInterval && clearInterval(window.ledInterval);
 
        const face = document.getElementById('cube_front');
 
        let t = 0;
        const size = 300;
        const r = {r}, g = {g}, b = {b};
        const solidColor  = `rgb(${{r}},${{g}},${{b}})`;
        const glowColor   = `rgba(${{r}},${{g}},${{b}},0.2)`;
 
        window.ledInterval = setInterval(() => {{
 
            const perimeter = 4 * size;
            let pos = (t % perimeter);
 
            let x = 0;
            let y = 0;
 
            if (pos < size) {{
                x = pos;
                y = 0;
            }} else if (pos < 2 * size) {{
                x = size;
                y = pos - size;
            }} else if (pos < 3 * size) {{
                x = size - (pos - 2 * size);
                y = size;
            }} else {{
                x = 0;
                y = size - (pos - 3 * size);
            }}
 
            face.style.background = `
                radial-gradient(circle at ${{x}}px ${{y}}px,
                ${{solidColor}} 0%,
                ${{solidColor}} 5%,
                ${{glowColor}} 15%,
                transparent 30%)
            `;
 
            face.style.backgroundColor = "rgba(0,0,0,0.1)";
 
            t += 8;
 
        }}, 30);
    """)


def stop_effects():

    # Update Cube Rendering
    ui.run_javascript("""
        clearInterval(window.ledInterval);
        window.snakeRunning = false;
        
        const face = document.getElementById('cube_front');
 
        if (face) {
            // Remove radial glow
            face.style.background = '';
            face.style.backgroundColor = '';
 
            // Reset to default cube styling
            face.style.border = '';
            face.style.boxShadow = '';
        }
 
        // Also reset all faces in case other effects were active
        document.querySelectorAll('.face').forEach(f => {
            f.style.background = '';
            f.style.border = '';
            f.style.boxShadow = '';
            f.style.opacity = '';
            f.style.filter = '';
        });
    """)




def set_all_faces_color(color):

    global manual_color

    manual_color = color

    for band in bands:
        band["color"] = color

    update_cube_colors()

    r = int(color[1:3], 16)
    g = int(color[3:5], 16)
    b = int(color[5:7], 16)

    ui.run_javascript(f"""
        if (window.snakeRunning) {{
            window.snakeColor = {{ r: {r}, g: {g}, b: {b} }};
        }}
    """)

    # Send Command(s) to ESP32
    SF.send_hues_from_hex_list([color])


# -------------------------------------------------
# STYLING
# -------------------------------------------------

ui.add_head_html("""
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
    0% { color: #ff0000; }
    33% { color: #00ff00; }
    66% { color: #0000ff; }
    100% { color: #ff0000; }
}

{
    box-sizing: border-box;
}

</style>
""")

# -------------------------------------------------
# MAIN LAYOUT
# -------------------------------------------------

with ui.column().classes("w-[1024px] h-[600px] mx-auto gap-2"):
    ui.label("∞ Infinity Cube ∞").classes("infinity-title w-full text-center")
    ui.separator()

    # Navigation Buttons
    with ui.row().classes("w-full justify-center gap-4"):
        btn_freq = ui.button("Frequency Band Control")
        btn_manual = ui.button("Manual Color Control")

    # -------------------------------------------------
    # MAIN SPLIT (ALWAYS VISIBLE)
    # -------------------------------------------------

    with ui.row().classes("w-full flex-1 no-wrap gap-2"):

        # =========================
        # LEFT SIDE (SWAPS)
        # =========================
        with ui.column().classes("w-1/2 h-full gap-2"):

            frequency_page = ui.column().classes("w-full")
            manual_page = ui.column().classes("w-full hidden")

            # -------- FREQUENCY PAGE --------
            with frequency_page:

                ui.label("Frequency Band Control").classes(
                    "text-lg font-semibold text-gray-200 text-center"
                )

                for i in range(SP.NUM_BANDS):
                    with ui.row().classes("items-center gap-4 w-full"):
                        ui.label(f"Band {i + 1}").classes(
                            "text-xs text-gray-400 w-16"
                        )

                        slider = ui.range(
                            min=0,
                            max=round(SP.MAX_FREQ),
                            value={
                                "min": bands[i]["min_freq"],
                                "max": bands[i]["max_freq"],
                            },
                        ).classes("flex-1")

                        value_label = ui.label(
                            f"{round(bands[i]['min_freq'])} - {round(bands[i]['max_freq'])} Hz"
                        ).classes("w-24 text-right text-gray-300")


                        def update_range(e, i=i, label=value_label):
                            min_val = e.value["min"]
                            max_val = e.value["max"]
                            bands[i]["min_freq"] = round(min_val)
                            bands[i]["max_freq"] = round(max_val)
                            label.set_text(f"{min_val} - {max_val} Hz")
                            check_overlap()

                            # Send Command(s) to ESP32
                            min_f = bands[i]["min_freq"]
                            max_f = bands[i]["max_freq"]
                            center = (min_f + max_f) / 2.0
                            SF.send_frequency(center)


                        slider.on_value_change(update_range)


                        def _make_color_picker(band_index: int, initial_color: str):
                            btn = ui.button().props("flat").classes("w-8 h-8 p-0 rounded")
                            btn.style(f"background-color: {initial_color}; border: 1px solid #888;")

                            input_id = f"color_input_{band_index}"

                            ui.html(f"""
                                <input type="color" id="{input_id}" value="{initial_color}"
                                    style="position:absolute;width:0;height:0;opacity:0;pointer-events:none;">
                            """)

                            def _on_change(e, idx=band_index, _btn=btn, _id=input_id):
                                hex_val = e.args
                                if not hex_val or not str(hex_val).startswith("#"):
                                    return
                                _name, snapped = SF.snap_to_ws2812(str(hex_val))
                                update_color(idx, snapped)
                                _btn.style(f"background-color: {snapped}; border: 1px solid #888;")

                            btn.on("click", lambda _id=input_id: ui.run_javascript(f"""
                                (function() {{
                                    const inp = document.getElementById('{_id}');
                                    inp.oninput = (ev) => {{
                                        emitEvent('color_changed_{_id}', ev.target.value);
                                    }};
                                    inp.click();
                                }})();
                            """))

                            ui.on(f"color_changed_{input_id}", _on_change)


                        _make_color_picker(i, bands[i]["color"])

            # -------- MANUAL PAGE --------
            with manual_page:

                ui.label("Manual Color Control").classes(
                    "text-lg font-semibold text-gray-200 text-center"
                )

                # --- COLOR GRID ---
                colors = [
                    SP.WS281_COLORS["Red"], SP.WS281_COLORS["Green"], SP.WS281_COLORS["Blue"],
                    SP.WS281_COLORS["Yellow"], SP.WS281_COLORS["Lavender"], SP.WS281_COLORS["Teal"],
                    SP.WS281_COLORS["White"], SP.WS281_COLORS["Orange"], SP.WS281_COLORS["Purple"],
                    SP.WS281_COLORS["Mint"], SP.WS281_COLORS["Dodger Blue"], SP.WS281_COLORS["Raspberry"]
                ]

                with ui.grid(columns=4).classes("gap-x-3 gap-y-18 w-72 mx-auto"):
                    for color in colors:
                        ui.button("") \
                            .props("flat") \
                            .classes("""
                                w-12 h-12
                                rounded-full
                                border-2 border-gray-700
                                shadow-md
                                !bg-transparent
                            """) \
                            .style(f"""
                                background-color: {color} !important;
                                box-shadow: 0 0 10px {color};
                            """) \
                            .on("click", lambda e, c=color: set_all_faces_color(c))

                ui.separator()

                # --- EFFECT BUTTONS ---
                with ui.row().classes("gap-x-3 gap-y-1 w-72 mx-auto"):
                    ui.button("Flash").on("click", start_flash)
                    ui.button("Strobe").on("click", start_strobe)
                    ui.button("Fade").on("click", start_fade)
                    ui.button("Smooth").on("click", start_smooth)
                    ui.button("Snake").on("click", start_snake)
                    ui.button("Stop").on("click", stop_effects)

        # =========================
        # RIGHT SIDE CUBE
        # =========================
        with ui.column().classes("w-1/2 h-full items-center justify-center").style("min-height: 400px; position: relative;"):

            ui.html("""
            <div class="scene">
              <div class="cube">
                <div class="face front" id="cube_front"></div>
                <div class="face back" id="cube_back"></div>
                <div class="face right" id="cube_right"></div>
                <div class="face left" id="cube_left"></div>
                <div class="face top" id="cube_top"></div>
                <div class="face bottom" id="cube_bottom"></div>
              </div>
            </div>

            <style>
            .scene {
                width: 300px;
                height: 300px;
                perspective: 1000px;
            }

            .cube {
                width: 100%;
                height: 100%;
                position: relative;
                transform-style: preserve-3d;
                animation: spin 30s infinite linear;
            }
            
            .face {
                position: absolute;
                width: 300px;
                height: 300px;
                background: rgba(0,255,255,0.05);
                border: 2px solid cyan;
                box-shadow: 0 0 20px cyan;
                filter: brightness(0.5);
                
                display: flex;
                align-items: center;
                justify-content: center;
            
                overflow: hidden;
            }

            .front  { transform: translateZ(150px); }
            .back   { transform: rotateY(180deg) translateZ(150px); }
            .right  { transform: rotateY(90deg) translateZ(150px); }
            .left   { transform: rotateY(-90deg) translateZ(150px); }
            .top    { transform: rotateX(90deg) translateZ(150px); }
            .bottom { transform: rotateX(-90deg) translateZ(150px); }

            @keyframes spin {
                from { transform: rotateX(0deg) rotateY(0deg); }
                to   { transform: rotateX(360deg) rotateY(360deg); }
            }
            </style>
            """)

    # -------------------------------------------------
    # ERROR + BRIGHTNESS
    # -------------------------------------------------

    error_label = ui.label("").classes(
        "text-red-500 text-center hidden"
    )

    ui.separator()

    brightness_label = ui.label("Brightness: 50%").classes(
        "text-sm text-gray-300 text-center"
    )

    ui.slider(
        min=0, max=100, value=50
    ).classes("w-full").on_value_change(
        lambda e: update_brightness(e.value)
    )

# Attach button actions AFTER elements exist
btn_freq.on("click", show_frequency)
btn_manual.on("click", show_manual)

ui.run()
