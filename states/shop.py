from bg import Background
from button import Button
from pyglet import image, sprite, text
from const import SCREEN_WIDTH, SCREEN_HEIGHT, FONT, switch_state, YELLOW

panel = image.load('graphics/misc/buy_panel.jpg')
product_board = image.load('graphics/misc/buy_unit_board.jpg')

right_panel_button_x = SCREEN_WIDTH - (128 + 10)
right_panel_button_start_y = SCREEN_HEIGHT - 100
board_start_x = 326
board_start_y = 560
board_gap_x = 30
board_gap_y = 64
button_w = 128
button_h = 32
board_w = 180
board_h = 120
columns = 5
board_font_size = 12
board_name_gap = 16
buy_button_x = 36
buy_button_y = 246


class Shop:
    def __init__(self):
        self.map = None
        self.panel = sprite.Sprite(panel, 0, 0)
        self.Buttons = [
            Button('graphics/Button_main.png', right_panel_button_x, right_panel_button_start_y, button_w, button_h,
                   resize=0,
                   text='Back', fontsize=16, fontname=FONT,
                   onClick=lambda: self.back()
                   ),  # 128/32 one sprite resolution
            Button('graphics/Button_main.png', buy_button_x, buy_button_y, button_w, button_h,
                   resize=0,
                   text='BUY', fontsize=16, fontname=FONT,
                   onClick=lambda: self.enterDeployemntMode()
                   ),  # 128/32 one sprite resolution
        ]
        self.balance = 0
        self.products = []
        self.boards = []
        self.chosen_product = None
        self.chosen_product_text = text.Label(' ',
                                              font_name=FONT,
                                              font_size=18,
                                              x=136, y=SCREEN_HEIGHT - 70,
                                              anchor_x='center',
                                              )
        self.balance_text = text.Label(f'Balance: {str(self.balance)}$',
                                       font_name=FONT,
                                       font_size=15,
                                       x=34, y=SCREEN_HEIGHT - 110,
                                       color=YELLOW
                                       )
        self.cost_text = text.Label(' ',
                                    font_name=FONT,
                                    font_size=15,
                                    x=128, y=SCREEN_HEIGHT - 132,
                                    color=(200, 30, 16, 255)
                                    )
        self.remain_text = text.Label(' ',
                                      font_name=FONT,
                                      font_size=15,
                                      x=142, y=SCREEN_HEIGHT - 154,
                                      color=YELLOW
                                      )

    def motion_update(self, mouse_x, mouse_y):
        for _button in self.Buttons:
            _button.update_motion(mouse_x, mouse_y)
        for board in self.boards:
            board.motion_update(mouse_x, mouse_y)

    def passive_update(self, dt):
        pass

    def press_update(self, mouse_x, mouse_y):
        for _button in self.Buttons:
            _button.update_press(mouse_x, mouse_y)
        for board in self.boards:
            board.press_update(mouse_x, mouse_y)

    def release_update(self, mouse_x, mouse_y):
        for _button in self.Buttons:
            _button.update_release(mouse_x, mouse_y)
        for board in self.boards:
            board.release_update(mouse_x, mouse_y)

    def draw(self):
        self.panel.draw()
        for _button in self.Buttons:
            _button.draw()
        for board in self.boards:
            board.draw()
        self.chosen_product_text.draw()
        self.cost_text.draw()
        self.balance_text.draw()
        self.remain_text.draw()

    def initProducts(self, map, products, start_balance):
        self.map = map
        self.products = products
        self.balance = start_balance
        self.balance_text.text = f'Balance: {start_balance}$'
        it = 0
        row = 0
        for product in self.products:
            self.boards.append(
                Board(
                    product,
                    board_start_x + (it * (board_w + board_gap_x)),
                    board_start_y - (row * (board_h + board_gap_y)),
                    board_w,
                    board_h)
            )
            it += 1
            if (it % columns == 0):
                row += 1
                it = 0

    def setChosenProduct(self, product):
        self.chosen_product = product
        self.chosen_product_text.text = product.name
        self.cost_text.text = f'-{product.price}$'
        self.remain_text.text = f'{self.balance - product.price}'

    def unsetChosenProduct(self):
        self.chosen_product = None
        self.chosen_product_text.text = ' '
        self.cost_text.text = ' '
        self.remain_text.text = ' '

    def back(self):
        switch_state(3)
        self.unsetChosenProduct()

    def enterDeployemntMode(self):
        self.map.setDeploymentMode(self.chosen_product.copy())
        self.back()

SHOP = Shop()


class Board:
    def __init__(self, unit, x, y, w, h):
        self.unit = unit
        self.x = x
        self.y = y
        self.price = unit.price
        self.name = unit.name
        self.unit.sprite.x = x + 32
        self.unit.sprite.y = y
        self.w = w
        self.h = h
        self.texture = sprite.Sprite(product_board, x, y)
        self.buy_button = Button('graphics/Button_main.png', self.x + self.w / 2 - button_w / 2, self.y - button_h - 5,
                                 button_w, button_h,
                                 resize=0,
                                 text='Piechota', fontsize=board_font_size, fontname=FONT,
                                 onClick=lambda: SHOP.setChosenProduct(self.unit)
                                 )  # 128/32 one sprite resolution
        self.price_text = text.Label(f'{self.price}$',
                                     font_name=FONT,
                                     font_size=board_font_size,
                                     x=self.x + w - 34, y=self.y + h - 22,
                                     anchor_x='center',
                                     color=(0, 0, 0, 255)
                                     )

    def motion_update(self, mouse_x, mouse_y):
        self.buy_button.update_motion(mouse_x, mouse_y)

    def press_update(self, mouse_x, mouse_y):
        self.buy_button.update_press(mouse_x, mouse_y)

    def release_update(self, mouse_x, mouse_y):
        self.buy_button.update_release(mouse_x, mouse_y)

    def draw(self):
        self.texture.draw()
        self.unit.sprite.draw()
        self.buy_button.draw()
        self.price_text.draw()
