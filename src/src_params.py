# ----------------------------------------------------------------
# File: src_ui.py
# Function: Industrial Control UI Layout with 3D Cube and Mapping Table
# Author: Connor Bastian, crb1759@rit.edu
# Date: February 12, 2026
# ----------------------------------------------------------------

# -------------------------------------------------
#           USER INTERFACE VARIABLES
# -------------------------------------------------

NUM_BANDS = 6
MAX_FREQ = 1000

BAND_STEP = int(MAX_FREQ) / int(NUM_BANDS)

# -------------------------------------------------
#               UART VARIABLES
# -------------------------------------------------

SERIAL_PORT = "dev/serial0"
BAUD_RATE = 115200
DATA_BITS = 8
PARITY = 'N'
STOP_BITS = 1

# LED UART Control Variables and Corresponding Effects

# -------------------------------------------------
# Example of Command That Can be Sent:
# E=5,N=3,H=20,80,140,B=180,F=440,S=25

# E=5 (Chase Effect),
# N=3 (# of Active Colors),
# H=20,80,140 (Hue List),
# B=180 (Brightness Value),
# F=440 (Frequency Value),
# S=25 (Speed Value)
# -------------------------------------------------

STROBE_CMD = 0
FADE_CMD = 1
FLASH_CMD = 2
SMOOTH_CMD = 3
RAINBOW_CMD = 4
CHASE_CMD = 5

COLOR_RANGE = range(1, 5)

HUE_RANGE = range(1, 5)

BRIGHTNESS_RANGE = range(0, 255)

SPEED_RANGE = range(1, 1000)

# -------------------------------------------------
# WS281 OBTAINABLE COLOR PALETTE
# Key   : human-readable name
# Value : hex string (#RRGGBB, uppercase)
# -------------------------------------------------

WS281_COLORS: dict[str, str] = {

    # ── Reds ──────────────────────────────────────
    "Red":                  "#FF0000",
    "Dark Red":             "#8B0000",
    "Crimson":              "#DC143C",
    "Firebrick":            "#B22222",
    "Indian Red":           "#CD5C5C",
    "Salmon":               "#FA8072",
    "Light Salmon":         "#FFA07A",
    "Tomato":               "#FF6347",
    "Coral":                "#FF7F50",

    # ── Oranges ───────────────────────────────────
    "Orange Red":           "#FF4500",
    "Orange":               "#FF8000",
    "Dark Orange":          "#FF6600",
    "Gold":                 "#FFD700",
    "Amber":                "#FFBF00",
    "Tangerine":            "#FF8C00",

    # ── Yellows ───────────────────────────────────
    "Yellow":               "#FFFF00",
    "Light Yellow":         "#FFFF80",
    "Lemon":                "#FFF44F",
    "Canary":               "#FFEF00",
    "Chartreuse":           "#7FFF00",
    "Yellow Green":         "#9ACD32",

    # ── Greens ────────────────────────────────────
    "Green":                "#00FF00",
    "Lime":                 "#00FF00",
    "Dark Green":           "#006400",
    "Forest Green":         "#228B22",
    "Medium Green":         "#00C800",
    "Olive":                "#808000",
    "Olive Drab":           "#6B8E23",
    "Spring Green":         "#00FF7F",
    "Medium Spring Green":  "#00FA9A",
    "Mint":                 "#00FF80",
    "Sea Green":            "#2E8B57",
    "Medium Sea Green":     "#3CB371",
    "Light Green":          "#90EE90",
    "Pale Green":           "#98FB98",
    "Lawn Green":           "#7CFC00",

    # ── Cyans ─────────────────────────────────────
    "Cyan":                 "#00FFFF",
    "Aqua":                 "#00FFFF",
    "Dark Cyan":            "#008B8B",
    "Teal":                 "#008080",
    "Light Cyan":           "#80FFFF",
    "Medium Turquoise":     "#48D1CC",
    "Turquoise":            "#40E0D0",
    "Dark Turquoise":       "#00CED1",
    "Aquamarine":           "#7FFFD4",
    "Medium Aquamarine":    "#66CDAA",
    "Cadet Blue":           "#5F9EA0",

    # ── Blues ─────────────────────────────────────
    "Blue":                 "#0000FF",
    "Dark Blue":            "#00008B",
    "Navy":                 "#000080",
    "Midnight Blue":        "#191970",
    "Medium Blue":          "#0000CD",
    "Royal Blue":           "#4169E1",
    "Cornflower Blue":      "#6495ED",
    "Steel Blue":           "#4682B4",
    "Dodger Blue":          "#1E90FF",
    "Deep Sky Blue":        "#00BFFF",
    "Sky Blue":             "#87CEEB",
    "Light Blue":           "#ADD8E6",
    "Powder Blue":          "#B0E0E6",
    "Light Steel Blue":     "#B0C4DE",
    "Slate Blue":           "#6A5ACD",
    "Medium Slate Blue":    "#7B68EE",
    "Blue Violet":          "#8A2BE2",

    # ── Purples & Violets ─────────────────────────
    "Violet":               "#EE82EE",
    "Purple":               "#800080",
    "Dark Purple":          "#4B0082",
    "Medium Purple":        "#9370DB",
    "Indigo":               "#4B0082",
    "Dark Violet":          "#9400D3",
    "Dark Orchid":          "#9932CC",
    "Medium Orchid":        "#BA55D3",
    "Orchid":               "#DA70D6",
    "Plum":                 "#DDA0DD",
    "Thistle":              "#D8BFD8",
    "Lavender":             "#C080FF",

    # ── Magentas & Pinks ──────────────────────────
    "Magenta":              "#FF00FF",
    "Fuchsia":              "#FF00FF",
    "Dark Magenta":         "#8B008B",
    "Hot Pink":             "#FF69B4",
    "Deep Pink":            "#FF1493",
    "Light Pink":           "#FFB6C1",
    "Pink":                 "#FFC0CB",
    "Pale Violet Red":      "#DB7093",
    "Medium Violet Red":    "#C71585",
    "Rose":                 "#FF007F",
    "Raspberry":            "#C80064",

    # ── Whites & Near-Whites ──────────────────────
    "White":                "#FFFFFF",
    "Warm White":           "#FFD080",
    "Cool White":           "#C8E0FF",
    "Soft White":           "#FFE8C0",
    "Ghost White":          "#F0F0FF",

    # ── Mixed / Special ───────────────────────────
    "Electric Blue":        "#0080FF",
    "Electric Green":       "#00FF40",
    "Electric Purple":      "#BF00FF",
    "Neon Orange":          "#FF6000",
    "Neon Yellow":          "#DFFF00",
    "Neon Pink":            "#FF0080",
    "Ice Blue":             "#80C0FF",
    "Peach":                "#FF8060",
    "Apricot":              "#FFA060",
    "Lilac":                "#C080C0",
    "Periwinkle":           "#8080FF",
    "Seafoam":              "#40FFA0",
    "Jade":                 "#00A86B",
    "Emerald":              "#00C060",
    "Sapphire":             "#0040C0",
    "Ruby":                 "#C00040",
    "Topaz":                "#FFC040",
    "Amethyst":             "#9966CC",
}