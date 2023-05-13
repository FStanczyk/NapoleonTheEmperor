from pyglet import *
from const import level

scale = level["scaling"]
class Animation:
    def __init__(self, spritesheet, w, h, frames_len, frame_delay, start_x=0, start_y=0):
        self.pending = False
        self.x = 120
        self.y = 120
        self.w = w * scale
        self.h = h * scale
        self.frames_len = frames_len
        self.frame_delay = frame_delay
        self.start_x = start_x
        self.start_y = start_y
        img = image.load(spritesheet)
        self.texture = img.get_texture()
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)

        self.texture.width *= scale
        self.texture.height *= scale
        self.frames = []
        self.time_since_last_frame = 0
        self.current_frame_index = 0
        for i in range(frames_len):
            self.frames.append(self.texture.get_region(self.start_x + self.w*i, self.start_y, self.w, self.h))
        self.current_frame = self.frames[0]
        self.sprite = sprite.Sprite(self.current_frame, x=self.x, y=self.y)

    def update(self, dt):
        self.time_since_last_frame += dt
        if self.time_since_last_frame > self.frame_delay:
            self.time_since_last_frame -= self.frame_delay
            self.current_frame_index = (self.current_frame_index + 1) % self.frames_len
            self.current_frame_time = 0
            self.sprite.image = self.frames[self.current_frame_index]

    def draw(self, dt):
        # update elapsed time since last frame
        self.time_since_last_frame += dt

        # update current frame if enough time has passed
        if self.current_frame_index >= self.frames_len - 1: self.pending = False; self.current_frame_index = 0

        if self.pending is True:
            if self.time_since_last_frame >= self.frame_delay:
                self.current_frame_index = (self.current_frame_index + 1) % self.frames_len
                self.current_frame = self.frames[self.current_frame_index]
                self.sprite.image = self.current_frame
                self.time_since_last_frame = 0
            self.sprite.draw()


    def setPos(self, x, y):
        self.x = x
        self.y = y
        self.sprite.x = x
        self.sprite.y = y

    def startAtPos(self, x, y):
        self.setPos(x,y)
        self.pending = True




explosionAnimation1 = Animation('graphics/animations/explosion.png',64,64,6,0.01)
explosionAnimation2 = Animation('graphics/animations/explosion.png',64,64,6,0.01)