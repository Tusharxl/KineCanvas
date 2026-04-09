# config.py

# This defines our UI buttons at the top of the screen.
# 'coord' dictates the start and end X-coordinates for the clickable areas.
COLORS_PALETTE = [
    {"name": "RED", "color": (0, 0, 255), "coord": (0, 100)},
    {"name": "BLUE", "color": (255, 0, 0), "coord": (100, 200)},
    {"name": "GREEN", "color": (0, 255, 0), "coord": (200, 300)},
    {"name": "YELLOW", "color": (0, 255, 255), "coord": (300, 400)},
    {"name": "CLEAR", "color": (50, 50, 50), "coord": (400, 550)}
]

# Tuning parameters for gestures
ERASER_RADIUS = 20        # The "vacuum" strength. Increase for a wider erasing area.
PINCH_THRESHOLD = 40      # How close the thumb and index finger need to be to grab a line.
WIPE_THRESHOLD = 1000     # How much distance the hand must travel to trigger a full screen wipe.