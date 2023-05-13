from bg import Background
from button import Button
from const import SCREEN_WIDTH, SCREEN_HEIGHT, FONT, switch_state, switch_level, level
from states.game import GAME, Game
names = ['Test1', 'Test2','Test3', 'Test4','Test5', 'Test6', 'Test2','Test3', 'Test4','Test5', 'Test6', 'Test2','Test3', 'Test4','Test5', 'Test6']
x_offset = SCREEN_WIDTH / 3
x_gap = 24
y_topPadding = 128
y_gap = 24
y_bottomPadding = 128
rows = 8

def start_level(levelId):
    switch_level(levelId)
    GAME.__init__()


class Level_Explorer:
    def __init__(self):
        self.bg = Background('graphics/bg/1.png', 'graphics/bg/3.png', 'graphics/bg/4.png')

        self.Buttons = []

        col = 0
        row = 0
        for b in range (len(names)):
            if(row > rows):
                row = 0
                col += 1
            self.Buttons.append(
                Button('graphics/Button_main.png',
                       (SCREEN_WIDTH / 2) - x_offset + (col * (128+x_gap)),
                       SCREEN_HEIGHT - y_topPadding - ((32+y_gap)* row+1),
                       128, 32,
                       resize=0,
                       text=names[b], fontsize=16, fontname=FONT,
                       onClick=lambda  lvlId=b: start_level(lvlId)
                       ),  # 128/32 one sprite resolution
            )
            row += 1


    def motion_update(self, mouse_x, mouse_y):
        for _button in self.Buttons:
            _button.update_motion(mouse_x, mouse_y)

    def passive_update(self, dt):
        self.bg.update()

    def press_update(self, mouse_x, mouse_y):
        for _button in self.Buttons:
            _button.update_press(mouse_x, mouse_y)

    def release_update(self, mouse_x, mouse_y):
        for _button in self.Buttons:
            _button.update_release(mouse_x, mouse_y)

    def draw(self):
        self.bg.draw()
        for _button in self.Buttons:
            _button.draw()


LEVEL_EXPLORER = Level_Explorer()



