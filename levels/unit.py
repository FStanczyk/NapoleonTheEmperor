from pyglet import graphics, image, text
from pyglet.gl import *
glEnable(GL_BLEND)
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
from const import FONT
scale = 1.8
w = 64* scale
h = (64 - 6)* scale

hp_board_player = image.load('graphics/misc/hp_board_0.png')
hp_board_enemy = image.load('graphics/misc/hp_board_1.png')

class Unit():

    def __init__(self, batch, group, texture):
        self.unit_id = -1
        self.owner = -1
        self.moved = False
        self.attacked = False
        self.nation = None
        self.destroyed = False
        self.name = None
        self.type = None
        self.tempSpotted = False
        self.texture =  image.load(texture)
        self.blit =  self.texture.get_texture()
        self.blit.width = w
        self.blit.height = h
        self.baseMoveRange = 0
        self.strength = 0
        self.experience = 0
        self.hp = 10
        self.x = 0
        self.y = 0
        self.sprite = pyglet.sprite.Sprite(self.blit, x=self.x, y=self.y, batch=batch, group=group)
        self.banner = hp_board_player if self.owner == 0 else hp_board_enemy
        self.banner_blit = self.banner.get_texture()
        self.banner_blit.width = w
        self.banner_blit.height = h
        self.banner_sprite = pyglet.sprite.Sprite(self.banner_blit, x=self.x, y=self.y, batch=batch, group=group)

        self.selected_cords_text = text.Label(str(self.hp),
                                              font_name=FONT,
                                              font_size=12,
                                              x=self.x + w/2, y=self.y + h/2 - (h/4 + 3),
                                              anchor_x='center',
                                              anchor_y='center',
                                              color=(0,0,0,255),
                                              batch=batch,
                                              group=group
                                              )

    # def draw(self):
    #     self.sprite.draw()

    def endTurn(self):
        self.moved = False
        self.attacked = False
        self.tempSpotted = False

    def attack(self):
        if not self.attacked:
            self.tempSpotted = True
            self.attacked = True
            return self.strength
        return 0

    def hit(self, strength):
        self.hp -= strength
        self.selected_cords_text.text = str(self.hp)
        if self.hp <= 0:
            self.destroyed = True

    def move(self, x, y):
        self.x = x
        self.y = y
        self.sprite.x = self.x
        self.sprite.y = self.y
        self.banner_sprite.x = self.x
        self.banner_sprite.y = self.y
        self.selected_cords_text.x = self.x + w/2
        self.selected_cords_text.y = self.y + h/2 - (h/4 + 3)

    def upgradeExperience(self, amount):
        self.experience += amount

