∞ Infinity Cube Industrial Control UI

An interactive industrial-style control interface built with **NiceGUI** that allows real-time manipulation of a 3D animated infinity cube using frequency bands and manual LED controls.

---

# Overview

This project provides:

- Frequency band control with overlap detection  
- Manual LED-style color selection  
- LED lighting effects (Flash, Strobe, Fade, Smooth)  
- Adjustable brightness control  
- Fully animated responsive 3D cube  
- Clean split-layout industrial UI  

The cube visually reflects color and brightness settings in real time.

---

# Project Structure

  src_main.py # Application entry point
  src_ui.py # UI layout and visual components
  src_func.py # Helper functions (e.g., rainbow generation)
  src_params.py # Configuration constants

---

# Features

# Frequency Band Control

- Adjustable frequency ranges per band
- Individual color selection per band
- Automatic frequency overlap detection
- Real-time cube face updates

Each frequency band maps directly to a cube face color.

---

# Manual Color Control

- LED remote-style preset color buttons
- One-click full cube color override
- Built-in lighting effects:

  - Flash
  - Strobe
  - Fade
  - Smooth
  - Stop

Effects are powered via JavaScript intervals injected through NiceGUI.

---

# Brightness Control

- Slider-based brightness adjustment
- Real-time dimming applied per cube face
- Preserves 3D rendering integrity
- Smooth visual transitions

---

# Responsive 3D Cube

- Continuous 3D rotation animation
- Preserves `transform-style: preserve-3d`
- Automatically resizes based on window width
- Maintains correct perspective proportions

---

# Requirements

- Python 3.9+
- NiceGUI

# Install dependencies:

- bash
- pip install nicegui

# Running the Project:

- python src_main.py
