import pyglet
from pyglet import *
FPS = 60.0  # less then 20 seems very unpleasant
SCREEN_WIDTH = 1520
SCREEN_HEIGHT = 720
MOVEABLE_WINDOW_W = 1520
MOVEABLE_WINDOW_H = 720
MOVE_MARGIN = 10
GUI_TOP_HEIGHT = 54
GUI_TOP = SCREEN_HEIGHT - GUI_TOP_HEIGHT
GUI_BOTTOM = 46
GUI_LEFT = 29
GUI_RIGHT_WIDTH = 134
GUI_RIGHT = SCREEN_WIDTH - GUI_RIGHT_WIDTH
YELLOW = (200, 142, 49, 255)
RED = (255, 17, 49, 255)
FONT = 'VCR osd mono'
STATES = ["boot_up",
          "level_explorer",
          "bot_creator",
          "game",
          "shop"]

LEVELS = [
    "Tutorial"
]

TERRAINS = {
    0: "field",
    1: "forest",
    2: "mountain",
    3: "beach",
    4: "sea",
    5: "river",
    6: "river_bridge",
    7: "city",
    8: "desert",
    9: "swamp"
}
TERRAINS_ROUGHNESS = {
    0: 2,
    1: 3,
    2: 4,
    3: 2,
    4: 2,
    5: 4,
    6: 1,
    7: 2,
    8: 2,
    9: 3
}
LOADING = False
state = STATES[0]
level = LEVELS[0]
window = pyglet.window.Window(SCREEN_WIDTH, SCREEN_HEIGHT)

MOVE_VELOCITY = 15


def set_loading(loading):
    global LOADING
    LOADING = loading


def switch_state(_id):
    global state
    state = STATES[_id]
    print("switched to: " + state)

def switch_level(_id):
    global level
    level = LEVELS[_id]
    print("started level: " + level)

