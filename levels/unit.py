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
        self.upgraded = False
        self.name = None
        self.type = None
        self.tempSpotted = False
        self.price = 0
        self.batch = batch
        self.group = group
        self.img = texture
        self.texture =  image.load(self.img)
        self.blit =  self.texture.get_texture()
        self.blit.width = w
        self.blit.height = h
        self.baseMoveRange = 0
        self.baseSpotRange = 0
        self.strength = 0
        self.experience = 0
        self.hp = 10
        self.x = 0
        self.y = 0
        self.row = 0
        self.col = 0
        self.sprite = pyglet.sprite.Sprite(self.blit, x=self.x, y=self.y) #, batch=batch, group=group)
        self.banner = hp_board_player if self.owner == 0 else hp_board_enemy
        self.banner_blit = self.banner.get_texture()
        self.banner_blit.width = w
        self.banner_blit.height = h
        self.banner_sprite = pyglet.sprite.Sprite(self.banner_blit, x=self.x, y=self.y)#, batch=batch, group=group)

        self.selected_cords_text = text.Label(str(self.hp),
                                              font_name=FONT,
                                              font_size=12,
                                              x=self.x + w/2, y=self.y + h/2 - (h/4 + 3),
                                              anchor_x='center',
                                              anchor_y='center',
                                              color=(0,0,0,255))#,
                                             # batch=batch,
                                             # group=group
                                             # )
    def draw(self):
        self.sprite.draw()
        self.banner_sprite.draw()
        self.selected_cords_text.draw()

    def endTurn(self):
        self.moved = False
        self.attacked = False
        self.upgraded = False
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

    def upgrade(self, expamount, hpamount):
        if not self.upgraded and not self.moved and not self.attacked:
            self.experience += expamount
            if self.experience > 10: self.experience = 10
            self.hp += hpamount
            self.selected_cords_text.text = str(self.hp)
            if self.hp > 18: self.hp = 18
            self.upgraded = True
            self.moved = True
            self.attacked = True

    def copy(self):
        # create a new instance of the class
        new_unit = Unit(self.batch, self.group, self.img)

        # copy all attributes from the original instance to the new instance
        new_unit.__dict__.update(self.__dict__)

        # create new sprite and label objects for the new instance
        new_unit.sprite = pyglet.sprite.Sprite(new_unit.blit, x=new_unit.x, y=new_unit.y)
        new_unit.banner_sprite = pyglet.sprite.Sprite(new_unit.banner_blit, x=new_unit.x, y=new_unit.y)
        new_unit.selected_cords_text = text.Label(str(new_unit.hp),
                                                  font_name=FONT,
                                                  font_size=12,
                                                  x=new_unit.x + w / 2, y=new_unit.y + h / 2 - (h / 4 + 3),
                                                  anchor_x='center',
                                                  anchor_y='center',
                                                  color=(0, 0, 0, 255))

        return new_unit