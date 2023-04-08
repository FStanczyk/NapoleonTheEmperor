from bg import Background
from button import Button
from pyglet import image, sprite, text
from const import SCREEN_WIDTH, SCREEN_HEIGHT, FONT, switch_state


class Boot_up:
    def __init__(self):
        self.bg = Background('graphics/bg/1.png', 'graphics/bg/3.png', 'graphics/bg/4.png')
        self.Buttons = [
            Button('graphics/Button_main.png', (SCREEN_WIDTH / 2) - 128 / 2, SCREEN_HEIGHT / 3, 128, 32,
                   resize=0,
                   text='START', fontsize=16, fontname=FONT,
                   onClick=lambda: switch_state(1)
                   ),  # 128/32 one sprite resolution
        ]
        self.logo_text = text.Label('Bonaparte the Emperor',
                                    font_name=FONT,
                                    font_size=78,
                                    x=SCREEN_WIDTH / 2, y=SCREEN_HEIGHT - 50,
                                    anchor_x='center',
                                    anchor_y='center'
                                    )
        self.column = sprite.Sprite(image.load('graphics/column.png'), SCREEN_WIDTH / 2 - 100, 0)

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
        self.logo_text.draw()
        self.column.draw()
        for _button in self.Buttons:
            _button.draw()


BOOT_UP = Boot_up()



