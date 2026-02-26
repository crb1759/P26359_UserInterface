# ----------------------------------------------------------------
# File: src_ui.py
# Function: Industrial Control UI Layout with 3D Cube and Mapping Table
# Author: Connor Bastian, crb1759@rit.edu
# Date: February 12, 2026
# ----------------------------------------------------------------

# .face {
            #     position: absolute;
            #     width: 300px;
            #     height: 300px;
            #     background: rgba(0,255,255,0.05);
            #     border: 2px solid cyan;
            #     box-shadow: 0 0 20px cyan;
            # }

# -------------------------------------------------
#           USER INTERFACE VARIABLES
# -------------------------------------------------

NUM_BANDS = 12

# -------------------------------------------------
#               UART VARIABLES
# -------------------------------------------------

BAUD_RATE = 115200
DATA_BITS = 8
PARITY = 'N'
STOP_BITS = 1
