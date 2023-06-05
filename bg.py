import pyglet
from pyglet.gl import *
glEnable(GL_TEXTURE_2D)
import const

BG_SPEED = 0.5  # pixel per frame
DISPARSE = 0.5  # difference in speed between textures, looks best when integers

class Background:
    def __init__(self, path1, path2=None, path3=None):
        self.pack = []
        self.help_pack = []

        for path in (path1, path2, path3):
            if path is not None:
                image_ = pyglet.image.load(path)
                image = image_.get_texture()
                image.width = const.SCREEN_WIDTH
                image.height = const.SCREEN_HEIGHT
                sprite = pyglet.sprite.Sprite(image)
                self.pack.append(sprite)
                self.help_pack.append(pyglet.sprite.Sprite(image))

        for txt in self.help_pack:
            txt.x = 0 - const.SCREEN_WIDTH

        if path2 is not None:
            self.pack.append(pyglet.sprite.Sprite(pyglet.image.load(path2)))
            self.help_pack.append(pyglet.sprite.Sprite(pyglet.image.load(path2)))
        if path3 is not None:
            self.pack.append(pyglet.sprite.Sprite(pyglet.image.load(path3)))
            self.help_pack.append(pyglet.sprite.Sprite(pyglet.image.load(path3)))

        for txt in(self.help_pack):
            txt.x = 0 - const.SCREEN_WIDTH


    def update(self):
        cnt = 1
        for i in range(len(self.pack)):
            self.pack[i].x = self.pack[i].x + BG_SPEED * cnt
            self.help_pack[i].x = self.help_pack[i].x + BG_SPEED * cnt

            if self.pack[i].x >= const.SCREEN_WIDTH:
                self.pack[i].x = 0 - const.SCREEN_WIDTH
            if self.help_pack[i].x >= const.SCREEN_WIDTH:
                self.help_pack[i].x = 0 - const.SCREEN_WIDTH

            cnt = cnt + DISPARSE


    def draw(self):
        for i in range(len(self.pack)):
            self.pack[i].draw()
            self.help_pack[i].draw()
