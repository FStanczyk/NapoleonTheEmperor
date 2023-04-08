from pyglet import image

import pyglet.text


class Button:
    '''
        img - path to the sprite_sheet
        x, y - coordinates (0,0 = bottom left corner)
        w, h - height and width of single sprite

        spritesheet guideline:
            should contain three states: 0 passive, 1 hover, 2 clicked
            should be a .png/.jpg file where three sprite are in a column
    '''

    def __init__(self, img, x, y, w, h, resize=0, text="default", fontsize=36, fontname='Times New Roman',
                 onClick=None, startX=0, startY=0):
        self.texture = image.load(img)
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.resize = resize
        self.text = text
        self.fontsize = fontsize
        self.fontname = fontname
        self.onClick = onClick
        self.start_x = startX
        self.start_y = startY
        self.states = [
            self.texture.get_region(self.start_x, self.start_y, w, h),  # passive
            self.texture.get_region(self.start_x, self.start_y+h, w, h),  # hover
            self.texture.get_region(self.start_x, self.start_y+h * 2, w, h)  # clicked
        ]
        self.active = self.states[0]

        self._text = pyglet.text.Label(self.text,
                                       font_name=self.fontname,
                                       font_size=self.fontsize,
                                       x=self.x + self.w / 2, y=self.y + self.h / 2,
                                       anchor_x='center',
                                       anchor_y='center'
                                       )

    def update_motion(self, mouse_x, mouse_y):
        if self.x <= mouse_x <= self.x + self.w and self.y <= mouse_y <= self.y + self.h:
            self.active = self.states[1]
        else:
            self.active = self.states[0]

    def update_press(self, mouse_x, mouse_y):
        if self.x <= mouse_x <= self.x + self.w and self.y <= mouse_y <= self.y + self.h:
            self.active = self.states[2]
        else:
            self.active = self.states[0]

    def update_release(self, mouse_x, mouse_y):
        if self.x <= mouse_x <= self.x + self.w and self.y <= mouse_y <= self.y + self.h:
            self.active = self.states[1]
            self.onClick()
        else:
            self.active = self.states[0]

    def draw(self):
        self.active.blit(self.x, self.y)
        self._text.draw()

