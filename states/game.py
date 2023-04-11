from bg import Background
from button import Button
from pyglet import image, sprite, text, shapes, clock
import pyglet
from levels.abstract_level import LEVELS
from const import SCREEN_WIDTH, SCREEN_HEIGHT, FONT, YELLOW, level, GUI_TOP_HEIGHT, GUI_RIGHT, GUI_RIGHT_WIDTH
from pyglet.window import mouse

gui =  image.load('graphics/maps/gui_bg.png')
exp_medal = image.load('graphics/misc/experience.png')
coin = image.load('graphics/misc/coin.png')
info_top_y = SCREEN_HEIGHT - GUI_TOP_HEIGHT/2.5
terrain_x = SCREEN_WIDTH / 9
coin_wh = 40
coin_x = SCREEN_WIDTH - SCREEN_WIDTH/3
coin_y = 3
exp_w = 12
exp_h = 17
exp_x = SCREEN_WIDTH - SCREEN_WIDTH/6
exp_y = 25
exp_gap = exp_w + 4
exp_blit = exp_medal.get_texture()
unit_name_x = SCREEN_WIDTH - SCREEN_WIDTH/3 + 48
unit_name_y = 25
exp_states = [
    exp_blit.get_region(0, 0, exp_w,exp_h),
    exp_blit.get_region(exp_w, 0, exp_w,exp_h),
    exp_blit.get_region(exp_w*2, 0, exp_w,exp_h)
    ]

buttons_x = GUI_RIGHT + GUI_RIGHT_WIDTH/2
gui_button_width = 80
gui_button_height = 40
gui_button_start_y = SCREEN_HEIGHT - 180
gui_button_gap = gui_button_height + 8
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
        self.coin = sprite.Sprite(coin, coin_x, coin_y)
        self.exp_set = [0,0,0,0,0]
        self.batch = pyglet.graphics.Batch()
        self.isUnitSelected = False
        self.unit_exp_set = [
            pyglet.sprite.Sprite(exp_states[self.exp_set[0]], x=exp_x, y=exp_y),
            pyglet.sprite.Sprite(exp_states[self.exp_set[1]], x=exp_x + exp_gap, y=exp_y),
            pyglet.sprite.Sprite(exp_states[self.exp_set[2]], x=exp_x + 2*exp_gap, y=exp_y),
            pyglet.sprite.Sprite(exp_states[self.exp_set[3]], x=exp_x + 3*exp_gap, y=exp_y),
            pyglet.sprite.Sprite(exp_states[self.exp_set[4]], x=exp_x + 4*exp_gap, y=exp_y),
        ]
        self.selected_terrain_text = text.Label(' ',
                                    font_name=FONT,
                                    font_size=18,
                                    x=terrain_x, y=info_top_y + 5,
                                    anchor_x='center',
                                    anchor_y='center',
                                    color = YELLOW
                                    )
        self.selected_cords_text = text.Label(' ',
                                    font_name=FONT,
                                    font_size=14,
                                    x=terrain_x, y=info_top_y - 16,
                                    anchor_x='center',
                                    anchor_y='center',
                                    color = YELLOW
                                    )
        self.end_turn_text = text.Label(' ',
                              font_name=FONT,
                              font_size=36,
                              x=SCREEN_WIDTH/2, y=SCREEN_HEIGHT/2,
                              anchor_x='center',
                              anchor_y='center'
                             )
        self.exp_text = text.Label('Experience',
                            font_name=FONT,
                            font_size=12,
                            x=exp_x - 8 , y=exp_y - 15,
                            color = YELLOW
                            )
        self.unit_name = text.Label('',
                                   font_name=FONT,
                                   font_size=12,
                                   x=unit_name_x, y=unit_name_y,
                                   color=YELLOW
                                   )
        self.unit_type = text.Label('',
                                   font_name=FONT,
                                   font_size=12,
                                   x=unit_name_x, y=unit_name_y - 14,
                                   color=YELLOW
                                   )
        rectangle = shapes.Rectangle(SCREEN_WIDTH, 0, 0, SCREEN_HEIGHT, color=(0, 0, 0), batch=self.batch)

        self.Buttons = [
            Button('graphics/misc/gui_button.jpg', buttons_x - gui_button_width/2,gui_button_start_y, gui_button_width, gui_button_height,
                   resize=0,
                   text='END', fontsize=16, fontname=FONT,
                   onClick=lambda: self.endMove(),
                   ),  # 128/32 one sprite resolution
            Button('graphics/misc/gui_button.jpg', buttons_x - gui_button_width / 2, gui_button_start_y - gui_button_gap,
                   gui_button_width, gui_button_height,
                   resize=0,
                   text='', fontsize=16, fontname=FONT,
                   startX = gui_button_width,
                   onClick=lambda: self.level.map.selectNextNotMovedUnit(),
                   ),  # 128/32 one sprite resolution
        ]

    def motion_update(self, mouse_x, mouse_y):
        self.level.map.motion_update(mouse_x, mouse_y)
        for _button in self.Buttons:
            _button.update_motion(mouse_x, mouse_y)

    def flicker_update(self, dt):
        self.level.map.flickerUpdate(dt)

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
        self.exp_set = [0, 0, 0, 0, 0]
        self.isUnitSelected = False
        if self.playerTurn == 0:
            self.level.map.release_update(mouse_x, mouse_y, button)
        if button & mouse.LEFT:
            if self.level.map.selectedHex: # allow only when some hex is selected
                self.selected_terrain_text.text = self.level.map.selectedHex.terrainType.upper()
                self.selected_cords_text.text = f"{self.level.map.selectedHex.row}, {self.level.map.selectedHex.col}"
                if self.level.map.selectedHex.unit is not None:
                    self.isUnitSelected = True
                    experience = self.level.map.selectedHex.unit.experience
                    name = self.level.map.selectedHex.unit.name
                    type = self.level.map.selectedHex.unit.type
                    self.unit_name.text = name
                    self.unit_type.text = type
                    set = self.calculateExpSprites(experience)
                    self.exp_set = set


        elif button & mouse.RIGHT:
            self.selected_terrain_text.text = ''
            self.selected_cords_text.text = ''

        for _button in self.Buttons:
            _button.update_release(mouse_x, mouse_y)

        self.unit_exp_set = [
            pyglet.sprite.Sprite(exp_states[self.exp_set[0]], x=exp_x, y=exp_y),
            pyglet.sprite.Sprite(exp_states[self.exp_set[1]], x=exp_x + exp_gap, y=exp_y),
            pyglet.sprite.Sprite(exp_states[self.exp_set[2]], x=exp_x + 2 * exp_gap, y=exp_y),
            pyglet.sprite.Sprite(exp_states[self.exp_set[3]], x=exp_x + 3 * exp_gap, y=exp_y),
            pyglet.sprite.Sprite(exp_states[self.exp_set[4]], x=exp_x + 4 * exp_gap, y=exp_y),
        ]


    def draw(self):
        if self.turnStarted:
            self.level.map.draw()
            self.gui.draw()
            self.selected_terrain_text.draw()
            self.selected_cords_text.draw()
            for _button in self.Buttons:
                _button.draw()
            if self.isUnitSelected is True:
                self.exp_text.draw()
                for exp in self.unit_exp_set:
                    exp.draw()
                self.coin.draw()
                self.unit_name.draw()
                self.unit_type.draw()




        if not self.turnStarted:
            self.end_turn_text.text = f" TURN {self.turn}"
            self.end_turn_text.draw()
            self.batch.draw()
            clock.schedule_once(self.setTurnReady, 1)

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

    def calculateExpSprites(self, experience):
        set = [0,0,0,0,0]
        m = experience
        it = 0
        while m > 0:
            if m >= 2:
                set[it] = 1
                m -= 2
            elif m == 1:
                set[it] = 2
                m -= 1
            it += 1
        return set


GAME = Game()
