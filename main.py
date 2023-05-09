import pyglet as pg
from pyglet.gl import *
from pyglet import window, app, clock
from states.boot_up import BOOT_UP
from states.level_explorer import LEVEL_EXPLORER
from states.game import GAME
from states.shop import SHOP
import const
window = const.window
# glEnable(GL_BLEND)
# glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

@window.event
def on_draw():
    window.clear()
    if const.state == "boot_up":
        BOOT_UP.draw()
    if const.state == "level_explorer":
        LEVEL_EXPLORER.draw()
    if const.state == "game":
        GAME.draw()
    if const.state == "shop":
        SHOP.draw()


@window.event
def update():
    if const.state == "boot_up":
        BOOT_UP.passive_update()
    if const.state == "level_explorer":
        LEVEL_EXPLORER.passive_update()
    if const.state == "game":
        GAME.passive_update()
        GAME.flicker_update()
    if const.state == "shop":
        SHOP.passive_update()

clock.schedule_interval(GAME.flicker_update, 1 / 2)
clock.schedule_interval(BOOT_UP.passive_update, 1 / const.FPS)
clock.schedule_interval(LEVEL_EXPLORER.passive_update, 1 / const.FPS)
clock.schedule_interval(GAME.passive_update, 1 / const.FPS)


#
# @window.event
# def slow_update(dt):
#     if const.state == "game":

@window.event
def on_mouse_press(mouse_x, mouse_y, button, modifiers):
    if const.LOADING:
        return
    if const.state == "boot_up":
        BOOT_UP.press_update(mouse_x, mouse_y)
    if const.state == "level_explorer":
        LEVEL_EXPLORER.press_update(mouse_x, mouse_y)
    if const.state == "game":
        GAME.press_update(mouse_x, mouse_y)
    if const.state == "shop":
        SHOP.press_update(mouse_x, mouse_y)



@window.event
def on_mouse_release(mouse_x, mouse_y, button, modifiers):
    if const.LOADING:
        return
    if const.state == "boot_up":
        BOOT_UP.release_update(mouse_x, mouse_y)
    if const.state == "level_explorer":
        LEVEL_EXPLORER.release_update(mouse_x, mouse_y)
    if const.state == "game":
        GAME.release_update(mouse_x, mouse_y, button)
    if const.state == "shop":
        SHOP.release_update(mouse_x, mouse_y)



@window.event
def on_mouse_motion(mouse_x, mouse_y, dx, dy):
    if const.LOADING:
        return
    if const.state == "boot_up":
        BOOT_UP.motion_update(mouse_x, mouse_y)
    if const.state == "level_explorer":
        LEVEL_EXPLORER.motion_update(mouse_x, mouse_y)
    if const.state == "game":
        GAME.motion_update(mouse_x, mouse_y)
    if const.state == "shop":
        SHOP.motion_update(mouse_x, mouse_y)



@window.event
def on_text(text):
    if const.LOADING:
        return


@window.event
def on_key_press(symbol, modifiers):
    if const.LOADING:
        return

app.run()
