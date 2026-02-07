"""Game config"""

# Window
FPS = 60
TITLE = "Dead End"
FULLSCREEN = True  # Borderless windowed

# Grid
TILE_SIZE = 32
GRID_WIDTH = 30
GRID_HEIGHT = 20
GRID_OFFSET_X = 50
GRID_OFFSET_Y = 50

# Colors (RGB)
COLOR_BG = (20, 20, 25)
COLOR_GRID = (40, 40, 50)
COLOR_GRID_HOVER = (60, 60, 75)
COLOR_PATH = (80, 70, 60)
COLOR_TOWER = (100, 150, 100)
COLOR_BARricade = (120, 100, 80)
COLOR_ENEMY = (150, 50, 50)
COLOR_START = (50, 150, 50)
COLOR_END = (150, 50, 50)
COLOR_UI_BG = (30, 30, 35)
COLOR_TEXT = (220, 220, 220)
COLOR_MONEY = (255, 215, 0)
COLOR_LIVES = (255, 80, 80)
COLOR_WAVE = (100, 200, 255)

# Game Settings
STARTING_MONEY = 150
STARTING_LIVES = 20
WAVE_DELAY = 3000  # ms between waves
BUILD_PHASE_TIME = 15000  # ms (optional timer)

# Tower Stats (MVP: 3 towers)
TOWERS = {
    "rifleman": {
        "name": "Rifleman",
        "cost": 50,
        "damage": 10,
        "range": 4,  # tiles
        "fire_rate": 0.5,  # seconds between shots
        "color": (100, 150, 100),
        "description": "Basic single-target damage"
    },
    "sniper": {
        "name": "Sniper",
        "cost": 100,
        "damage": 40,
        "range": 8,
        "fire_rate": 1.5,
        "color": (80, 80, 120),
        "description": "High damage, long range, slow"
    },
    "barricade": {
        "name": "Barricade",
        "cost": 25,
        "hp": 200,
        "color": (120, 100, 80),
        "description": "Blocks path, no attack"
    }
}

# Enemy Stats (MVP: 2 types)
ENEMIES = {
    "walker": {
        "name": "Walker",
        "hp": 30,
        "speed": 1.5,  # tiles per second
        "reward": 5,
        "color": (150, 50, 50),
        "radius": 10
    },
    "runner": {
        "name": "Runner",
        "hp": 15,
        "speed": 3.0,
        "reward": 8,
        "color": (200, 80, 60),
        "radius": 8
    }
}

# Wave Definitions (MVP)
WAVES = [
    {"walkers": 5, "runners": 0, "delay": 1000},
    {"walkers": 8, "runners": 2, "delay": 800},
    {"walkers": 12, "runners": 5, "delay": 700},
    {"walkers": 15, "runners": 10, "delay": 600},
    {"walkers": 20, "runners": 15, "delay": 500},
]
