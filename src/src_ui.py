# ----------------------------------------------------------------
# File: src_ui.py
# Function: Industrial Control UI Layout
# Author: Connor Bastian
# Date: February 12, 2026
# ----------------------------------------------------------------

from nicegui import ui
import src_params as SP
import src_func as SF

# -------------------------------------------------
# GLOBAL DATA
# -------------------------------------------------

rainbow = SF.generate_rainbow_colors(SP.NUM_BANDS)

bands = [
    {
        "min_freq": i * 20 + 1,
        "max_freq": (i + 1) * 20,
        "intensity": 50,
        "color": rainbow[i],
    }
    for i in range(SP.NUM_BANDS)
]

color_buttons = []
range_sliders = []


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
                error_label.set_text("⚠ Frequency ranges overlap!")
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
                face.style.background = '{color}33';
                face.style.border = '2px solid {color}';
                face.style.boxShadow = '0 0 20px {color}';
            }}
        """)


def update_color(index, value):
    bands[index]["color"] = value
    update_cube_colors()

    # Send Command(s) to ESP32
    selected = [band["color"] for band in bands[:5]]
    SF.send_hues_from_hex_list(selected)


# -------------------------------------------------
#               LED CONTROL FUNCTIONS
# -------------------------------------------------

def update_brightness(value):
    brightness_label.set_text(f"Brightness: {value}%")
    brightness_factor = value / 100

    # Send Command(s) to ESP32
    SF.send_brightness(int(value))

    ui.run_javascript(f"""
        const faces = document.querySelectorAll('.face');
        faces.forEach(face => {{
            face.style.filter = "brightness({brightness_factor})";
        }});
    """)


def start_flash():
    # Send Command(s) to ESP32
    SF.send_effect(2)
    SF.send_speed(250)

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
    SF.send_effect(0)
    SF.send_speed(100)

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
    SF.send_effect(1)
    SF.send_speed(30)

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
    SF.send_effect(3)
    SF.send_speed(18)

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
    ui.run_javascript("""
        window.ledInterval && clearInterval(window.ledInterval);

        const face = document.getElementById('cube_front');

        let t = 0;
        const size = 300;

        window.ledInterval = setInterval(() => {

            const perimeter = 4 * size;
            let pos = (t % perimeter);

            let x = 0;
            let y = 0;

            if (pos < size) {
                x = pos;
                y = 0;
            } else if (pos < 2 * size) {
                x = size;
                y = pos - size;
            } else if (pos < 3 * size) {
                x = size - (pos - 2 * size);
                y = size;
            } else {
                x = 0;
                y = size - (pos - 3 * size);
            }

            face.style.background = `
                radial-gradient(circle at ${x}px ${y}px,
                #00ff00 0%,
                #00ff00 5%,
                rgba(0,255,0,0.2) 15%,
                transparent 30%)
            `;

            face.style.backgroundColor = "rgba(0,0,0,0.1)";

            t += 8;

        }, 30);
    """)


def stop_effects():
    ui.run_javascript("""
        clearInterval(window.ledInterval);
        
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
    for band in bands:
        band["color"] = color
    update_cube_colors()

    # Send Command(s) to ESP32
    SF.send_hues_from_hex_list([color])


# -------------------------------------------------
# STYLING
# -------------------------------------------------

ui.add_head_html("""
<style>
body {
    background-color: #1E1E1E;
}

.infinity-title {
    font-size: 4rem;
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
</style>
""")

# -------------------------------------------------
# MAIN LAYOUT
# -------------------------------------------------

with ui.column().classes("w-full h-screen p-6 gap-6"):
    ui.label("∞ Infinity Cube ∞").classes("infinity-title w-full text-center")
    ui.separator()

    # Navigation Buttons
    with ui.row().classes("w-full justify-center gap-4"):
        btn_freq = ui.button("Frequency Band Control")
        btn_manual = ui.button("Manual Color Control")

    # -------------------------------------------------
    # MAIN SPLIT (ALWAYS VISIBLE)
    # -------------------------------------------------

    with ui.row().classes("w-full h-[70vh] no-wrap gap-6"):

        # =========================
        # LEFT SIDE (SWAPS)
        # =========================
        with ui.column().classes("w-1/2 h-full overflow-auto gap-4"):

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
                            max=240,
                            value=[
                                bands[i]["min_freq"],
                                bands[i]["max_freq"],
                            ],
                        ).classes("flex-1")

                        value_label = ui.label(
                            f"{bands[i]['min_freq']} - {bands[i]['max_freq']} Hz"
                        ).classes("w-24 text-right text-gray-300")


                        def update_range(e, i=i, label=value_label):
                            min_val, max_val = slider.value
                            bands[i]["min_freq"] = min_val
                            bands[i]["max_freq"] = max_val
                            label.set_text(f"{min_val} - {max_val} Hz")
                            check_overlap()

                            # Send Command(s) to ESP32
                            min_f = bands[i]["min_freq"]
                            max_f = bands[i]["max_freq"]
                            center = (min_f + max_f) / 2.0
                            SF.send_frequency(center)


                        slider.on_value_change(update_range)

                        color_btn = ui.button().props("flat")
                        color_btn.classes("w-8 h-8 p-0 rounded")
                        color_btn.style(
                            f"background-color: {bands[i]['color']}; border: 1px solid #888;"
                        )

                        with ui.menu().props('anchor="bottom left" self="top left"') as menu:
                            with ui.card().classes("bg-gray-900 p-2"):
                                picker = ui.color_picker(
                                    value=bands[i]["color"]
                                ).props("format=hex flat")


                                def apply_color(e, i=i):
                                    update_color(i, e.value)
                                    color_btn.style(
                                        f"background-color: {e.value}; border: 1px solid #888;"
                                    )
                                    menu.close()


                                picker.on_value_change(apply_color)

                        color_btn.on("click", menu.open)

            # -------- MANUAL PAGE --------
            with manual_page:

                ui.label("Manual Color Control").classes(
                    "text-lg font-semibold text-gray-200 text-center"
                )

                # --- COLOR GRID ---
                colors = [
                    "#FF0000", "#00FF00", "#0000FF",
                    "#FFFF00", "#FF00FF", "#00FFFF",
                    "#FFFFFF", "#FFA500", "#800080",
                    "#00FF7F", "#1E90FF", "#FF1493"
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
                with ui.row().classes("gap-x-3 gap-y-18 w-72 mx-auto"):
                    ui.button("Flash").on("click", start_flash)
                    ui.button("Strobe").on("click", start_strobe)
                    ui.button("Fade").on("click", start_fade)
                    ui.button("Smooth").on("click", start_smooth)
                    ui.button("Snake").on("click", start_snake)
                    ui.button("Stop").on("click", stop_effects)

        # =========================
        # RIGHT SIDE CUBE
        # =========================
        with ui.column().classes("w-1/2 h-full flex items-center justify-center"):

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
