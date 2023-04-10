from pyglet import graphics, image
from pyglet.gl import *
glEnable(GL_BLEND)
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
from const import MOVE_VELOCITY, TERRAINS
scale = 1.8
w = 64* scale
h = (64 - 6)* scale

texture = image.load('graphics/maps/hex.png')
blit = texture.get_texture()
blit.width *= scale
blit.height *= scale

class Hex():
    def __init__(self, row, col, batch, group):
        self.unit = None
        self.terrainType = TERRAINS[0] # standard is "field"
        self.isRoad = False
        self.flag = None
        self.name = None
        self.inMoveRange = False
        self.inAttackRange = False
        self.isMovable = True
        self.isVisible = False
        self.selected = False
        self.onOccupation = None
        self.row = row
        self.col = col
        self.x = col * (3*w/4) - w
        self.y = row * h - h
        if col %2 == 1:
            self.y += h/2

        self.states = [
            blit.get_region(0, 0, w, h),  # isVisible
            blit.get_region(w, 0, w, h),  # clicked - isVisible
            blit.get_region(2 * w, 0, w, h),  # not accessible
            blit.get_region(3 * w, 0, w, h)  # is not visible
        ]
        self.active = self.states[3]
        self.sprite = pyglet.sprite.Sprite(self.active, x=self.x, y=self.y, batch=batch, group=group)


    def drawUnit(self):
        if self.unit is not None:
            self.unit.draw()

    def release_update(self, mouse_x, mouse_y):
        if not self.isVisible:
            self.active = self.states[3]
        elif not self.isMovable:
            self.active = self.states[2]
        elif self.x <= mouse_x <= self.x + w and self.y <= mouse_y <= self.y + h:
            self.active = self.states[1]
            self.selected = True
        else:
            self.active = self.states[0]
            self.selected = False

        self.sprite.image = self.active

    def refreshHex(self):
        if not self.isVisible:
            self.active = self.states[3]
        elif not self.isMovable:
            self.active = self.states[2]
        else:
            self.active = self.states[0]
            self.selected = False

        self.sprite.image = self.active


    def move(self,dir):
        if dir in {'top', 'bottom'}:
            self.y += MOVE_VELOCITY if dir == 'top' else -MOVE_VELOCITY
        elif dir in {'left', 'right'}:
            self.x += MOVE_VELOCITY if dir == 'right' else -MOVE_VELOCITY

        self.sprite.x = self.x
        self.sprite.y = self.y
        if self.flag is not None:
            self.flag.move(self.x, self.y)
        if self.unit is not None:
            self.unit.move(self.x, self.y)

    def center(self):
        return [self.x + w/2, self.y + h/2]

    def deselect(self):
        self.selected = False
        self.active = self.states[0]
        self.sprite.image = self.active

    def placeUnit(self, unit):
        self.unit = unit
        self.unit.x = self.x
        self.unit.y = self.y

    def moveOutUnit(self):
        self.unit = None


class Flag:
    def __init__(self, batch, group, texture_path):
        self.texture = image.load(texture_path)
        print(texture_path)
        self.blit = self.texture.get_texture()
        self.blit.width = w
        self.blit.height = h
        self.x = 220
        self.y = 220
        self.sprite = pyglet.sprite.Sprite(self.blit, x=self.x, y=self.y, batch=batch, group=group)

    def move(self, x, y):
        print(self.x)
        self.x = x
        self.y = y
        self.sprite.x = x
        self.sprite.y = y
