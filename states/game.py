from bg import Background
from button import Button
from pyglet import image, sprite, text, shapes, clock
import pyglet
from levels.abstract_level import LEVELS
from const import SCREEN_WIDTH, SCREEN_HEIGHT, FONT, switch_state, level, GUI_TOP_HEIGHT, GUI_RIGHT, GUI_RIGHT_WIDTH
from pyglet.window import mouse
import time

gui =  image.load('graphics/maps/gui_bg.png')
info_top_y = SCREEN_HEIGHT - GUI_TOP_HEIGHT/2
terrain_x = SCREEN_WIDTH / 10 - 30

buttons_x = GUI_RIGHT + GUI_RIGHT_WIDTH/2
gui_button_width = 80
gui_button_height = 40
gui_button_start_y = SCREEN_HEIGHT - 180
class Game:

    def __init__(self):
        self.level = LEVELS[level]
        self.gameStarted = False
        self.gameFinished = False
        self.turnReady = False
        self.turnStarted = False
        self.turn = 0
        self.playerTurn = 0     # 0 - Player; 1 - AI
        self.gui = sprite.Sprite(gui, 0, 0)

        self.infos = []
        self.batch = pyglet.graphics.Batch()
        self.selected_terrain_text = text.Label(' ',
                                    font_name=FONT,
                                    font_size=18,
                                    x=terrain_x, y=info_top_y + 5,
                                    anchor_x='center',
                                    anchor_y='center'
                                    )
        self.selected_cords_text = text.Label(' ',
                                    font_name=FONT,
                                    font_size=14,
                                    x=terrain_x, y=info_top_y - 16,
                                    anchor_x='center',
                                    anchor_y='center'
                                    )
        self.end_turn_text = text.Label(' ',
                              font_name=FONT,
                              font_size=36,
                              x=SCREEN_WIDTH/2, y=SCREEN_HEIGHT/2,
                              anchor_x='center',
                              anchor_y='center',
                             )
        rectangle = shapes.Rectangle(SCREEN_WIDTH, 0, 0, SCREEN_HEIGHT, color=(0, 0, 0), batch=self.batch)

        self.Buttons = [
            Button('graphics/misc/gui_button.jpg', buttons_x - gui_button_width/2,gui_button_start_y, gui_button_width, gui_button_height,
                   resize=0,
                   text='END', fontsize=16, fontname=FONT,
                   onClick=lambda: self.endMove(),
                   ),  # 128/32 one sprite resolution
        ]

    def motion_update(self, mouse_x, mouse_y):
        self.level.map.motion_update(mouse_x, mouse_y)
        for _button in self.Buttons:
            _button.update_motion(mouse_x, mouse_y)

    def passive_update(self, dt):
        self.level.map.passive_update(dt)
        if not self.gameStarted and self.level != None:
            self.level.initLevel()
            self.gameStarted = True

        if not self.turnStarted and self.turnReady:
            self.startTurn()
            self.level.map.refreshTurnHexSprites()

    def press_update(self, mouse_x, mouse_y):
        self.level.map.press_update(mouse_x, mouse_y)
        for _button in self.Buttons:
            _button.update_press(mouse_x, mouse_y)

    def release_update(self, mouse_x, mouse_y, button):
        if self.playerTurn == 0:
            self.level.map.release_update(mouse_x, mouse_y, button)
        if button & mouse.LEFT:
            if self.level.map.selectedHex: # allow only when some hex is selected
                self.selected_terrain_text.text = self.level.map.selectedHex.terrainType
                self.selected_cords_text.text = f"{self.level.map.selectedHex.row}, {self.level.map.selectedHex.col}"
        elif button & mouse.RIGHT:
            self.selected_terrain_text.text = ''
            self.selected_cords_text.text = ''

        for _button in self.Buttons:
            _button.update_release(mouse_x, mouse_y)

    def draw(self):
        if self.turnStarted:
            self.level.map.draw()
            self.gui.draw()
            self.selected_terrain_text.draw()
            self.selected_cords_text.draw()
            for _button in self.Buttons:
                _button.draw()


        if not self.turnStarted:
            self.end_turn_text.text = f" TURN {self.turn}"
            self.end_turn_text.draw()
            self.batch.draw()
            clock.schedule_once(self.setTurnReady, 3)



    def startTurn(self):
        self.playerTurn = 0
        self.level.map.showSpottedHexes()
        print('started Turn')
        self.turnStarted = True

    def endTurn(self):
        self.level.map.unspotAllHexes()
        self.turn += 1
        self.level.map.endTurn()
        self.turnStarted = False

    def endMove(self):
        self.turnReady = False
        self.playerTurn = 1
        self.endTurn()

    def setTurnReady(self, dt):
        self.turnReady = True

GAME = Game()
