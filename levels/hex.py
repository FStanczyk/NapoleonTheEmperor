from pyglet import *
from const import MOVE_VELOCITY, TERRAINS, TERRAINS_ROUGHNESS, level
scale = level["hexScale"]
w = 64 * scale
h = (64 - 9)* scale

texture = image.load('graphics/maps/hex.png')
blit = texture.get_texture()
gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)

blit.width *= scale
blit.height *= scale


class Hex():
    def __init__(self, row, col, batch, group):
        self.w = w
        self.h = h
        self.unit = None
        self.terrainType = TERRAINS[0] # standard is "field"
        self.terrainRoughness = TERRAINS_ROUGHNESS[0]
        self.isRoad = False
        self.flag = None # also tells that it is a city
        self.name = ''
        self.inMoveRange = False
        self.inAttackRange = False
        self.isMovable = True
        self.isVisible = False
        self.selected = False
        self.isObjective = False
        self.onOccupation = None
        self.lastOccupant = -1
        self.row = row
        self.col = col
        self.x = col * (3*w/4) - w
        self.y = row * h - h
        self.absX = self.x # asbX/Y holds the x/y value of the initialized map, not being affected by mouse moving
        self.absY = self.y
        if col %2 == 1:
            self.y += h/2

        self.states = [
            blit.get_region(0, 0, w, h),  # isVisible
            blit.get_region(w, 0, w, h),  # clicked - isVisible
            blit.get_region(2 * w, 0, w, h),  # not accessible
            blit.get_region(3 * w, 0, w, h)  # is not visible
        ]
        self.active = self.states[3]
        self.sprite = sprite.Sprite(self.active, x=self.x, y=self.y, batch=batch, group=group)

    def drawUnit(self):
        if self.unit is not None:
            self.unit.draw()

    def release_update(self, mouse_x, mouse_y):
        if not self.isVisible:
            self.active = self.states[3]
        elif not self.isMovable:
            self.active = self.states[2]
        elif self.x <= mouse_x <= self.x + w and self.y <= mouse_y <= self.y + h:
            self.select()
        else:
            self.deselect()

        self.sprite.image = self.active

    def refreshHex(self):
        if not self.isVisible:
            self.active = self.states[3]
        elif not self.isMovable:
            self.active = self.states[2]
        else:
            self.deselect()

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


    def select(self):
        self.selected = True
        self.active = self.states[1]
        self.sprite.image = self.active

    def placeUnit(self, unit):
        self.unit = unit
        self.unit.x = self.x
        self.unit.y = self.y
        self.unit.row = self.row
        self.unit.col = self.col
        self.occupyFlag(unit.owner)


    def moveOutUnit(self):
        self.unit = None

    def occupyFlag(self, owner):
        if self.lastOccupant != owner:
            if self.flag is not None:
                self.flag.switchFlag(owner)
        self.lastOccupant = owner

class Flag:
    def __init__(self, batch, group, initialTexture, switchedTexture, initialOwner):
        self.initialTexture = image.load(initialTexture)
        self.switchedTexture = image.load(switchedTexture)
        self.initialBlit = self.initialTexture.get_texture()
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
        self.switchedBlit = self.switchedTexture.get_texture()
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)

        self.isFlickering = False
        self.initialBlit.width *= scale
        self.initialBlit.height *= scale
        self.switchedBlit.width *= scale
        self.switchedBlit.height *= scale
        self.blits = [self.initialBlit, self.switchedBlit]
        self.owner = initialOwner
        self.x = 0
        self.y = 0
        self.activeBlit = self.blits[0]
        self.states = [
            self.activeBlit.get_region(0, 0, w, h),
            self.activeBlit.get_region(w, 0, w, h),  # border light
        ]
        self.active = self.states[0]
        self.sprite = sprite.Sprite(self.active, x=self.x, y=self.y, batch=batch, group=group)

    def move(self, x, y):
        self.x = x
        self.y = y
        self.sprite.x = x
        self.sprite.y = y

    def ligthSwitch(self):
        if self.isFlickering is False: return
        if self.active is self.states[0]:
            self.active = self.states[1]
        else:
            self.active = self.states[0]
        self.sprite.image = self.active

    def switchFlag(self, owner):
        if self.activeBlit == self.blits[0]:
            self.activeBlit = self.blits[1]
        elif self.activeBlit == self.blits[1]:
            self.activeBlit = self.blits[0]

        self.states = [
            self.activeBlit.get_region(0, 0, w, h),
            self.activeBlit.get_region(w, 0, w, h),  # border light
        ]
        self.owner = owner
        self.active = self.states[0]
        self.sprite.image = self.active