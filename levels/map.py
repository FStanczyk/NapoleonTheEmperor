import pyglet
from pyglet.window import mouse
from pyglet import *
from levels.calculations import calculateDamage
from animation import explosionAnimation1, explosionAnimation2
from const import \
    FONT, YELLOW, RED, \
    MOVE_MARGIN, MOVE_VELOCITY, \
    SCREEN_HEIGHT, SCREEN_WIDTH, level, DEBUG_MODE
from levels.hex import Hex, Flag
import math
W_LEFT_MOVE = MOVE_MARGIN
W_RIGHT_MOVE = SCREEN_WIDTH - MOVE_MARGIN
H_TOP_MOVE = SCREEN_HEIGHT - MOVE_MARGIN
H_BOTTOM_MOVE = MOVE_MARGIN + 48
currentOccuranceX = SCREEN_WIDTH / 2
currentOccuranceY = SCREEN_HEIGHT - 120
textBatch = pyglet.graphics.Batch()

scale = level["scaling"]
hexScale = level["hexScale"]
class Map():
    def __init__(self, texturePath):
        image = pyglet.image.load(texturePath).get_texture()
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)

        image.width *= scale
        image.height *= scale

        self.batch = pyglet.graphics.Batch()
        self.group = pyglet.graphics.Group()
        self.map = pyglet.sprite.Sprite(image, batch=self.batch)
        self.hexMap = {}
        self.players = []
        rowsNeeded = math.ceil(int(image.height / 64))
        colsNeeded = math.ceil(int((image.width - 64/2)/64)) + 2

        for r in range(rowsNeeded):
            for c in range(colsNeeded):
                hex_key = f"{r},{c}"
                self.hexMap[hex_key] = Hex(r, c, self.batch, self.group)

        self.objectives = []

        self.overEdge = set()
        self.selectedHex = None

        self.heldUnit = None
        self.action__move = False
        self.action__attack = False
        self.deploymentMode = False
        self.currentOccurrence = text.Label('',
                                            font_name=FONT,
                                            font_size=12,
                                            x=currentOccuranceX, y=currentOccuranceY,
                                            color=YELLOW,
                                            batch=textBatch
                                            )
        self.borderLabel = text.Label('',
                                      font_name=FONT,
                                      font_size=12,
                                      x=currentOccuranceX, y=currentOccuranceY,
                                      color=(0, 0, 0, 255),
                                      # bold=True,
                                      batch=textBatch,
                                      )

    def draw(self):
        self.batch.draw()
        for _hex in self.hexMap.values():
            if _hex.isVisible is True:
                _hex.drawUnit()
        dt = clock.tick()
        explosionAnimation1.draw(dt)
        explosionAnimation2.draw(dt)

    def moveMap(self, dir):
        if self.action__attack is True: return
        if dir == 'top':
            self.map.y += MOVE_VELOCITY
        elif dir == 'bottom':
            self.map.y -= MOVE_VELOCITY
        elif dir == 'left':
            self.map.x -= MOVE_VELOCITY
        elif dir == 'right':
            self.map.x += MOVE_VELOCITY

        for hex in self.hexMap.values():
            hex.move(dir)

    def passive_update(self, dt):
        if 2 in self.overEdge and abs(self.map.x) < self.map.width - SCREEN_WIDTH:
            self.moveMap('left')
        elif 1 in self.overEdge and self.map.x < 0:
            self.moveMap('right')
        elif 3 in self.overEdge and abs(self.map.y) > 0:
            self.moveMap('top')
        elif 4 in self.overEdge and abs(self.map.y) < self.map.height - SCREEN_HEIGHT:
            self.moveMap('bottom')
        else:
            self.moveMap('none')

    def flickerUpdate(self, dt):
        for hex in self.hexMap.values():
            if hex.flag is not None:
                hex.flag.ligthSwitch()

    def motion_update(self, mouse_x, mouse_y):
        self.overEdge = set()
        if mouse_x > W_RIGHT_MOVE:
            self.overEdge.add(2)
        if mouse_x < W_LEFT_MOVE:
            self.overEdge.add(1)
        if mouse_y < H_BOTTOM_MOVE:
            self.overEdge.add(3)
        if mouse_y > H_TOP_MOVE:
            self.overEdge.add(4)

    def press_update(self, mouse_x, mouse_y):
        pass

    def release_update(self, mouse_x, mouse_y, button):
        if self.action__attack is True: return
        alreadyHeld = self.selectedHex
        if button & mouse.LEFT:
            self.calcSelectedHex(mouse_x, mouse_y)
        elif button & mouse.RIGHT:
            self.deselectHex()
            self.unsetDeploymentMode()

        self.action(alreadyHeld)
        self.deployUnit(self.selectedHex, self.heldUnit)
        self.unspotAllHexes()
        self.showVisibleHexes()
        self.refreshTurnHexSprites()

    def selectHex(self, hex):
        self.selectedHex = hex
        if self.selectedHex.unit is not None:
            self.action__move = True
            self.heldUnit = self.selectedHex.unit
        hex.select()

    def deselectHex(self):
        if self.selectedHex is not None:
            self.selectedHex.deselect()
            self.selectedHex = None
        self.action__move = False
        self.action__attack = False
        self.heldUnit = None

    def calcSelectedHex(self, mouse_x, mouse_y):
        selected = []
        for hex in self.hexMap.values():
            hex.release_update(mouse_x, mouse_y)
            if hex.selected: selected.append(hex)
        if len(selected) == 2:
            hex1 = selected[0]
            hex2 = selected[1]
            center1 = hex1.center()
            center2 = hex2.center()
            distance1 = ((mouse_x - center1[0]) ** 2 + (mouse_y - center1[1]) ** 2) ** 0.5
            distance2 = ((mouse_x - center2[0]) ** 2 + (mouse_y - center2[1]) ** 2) ** 0.5
            if distance1 < distance2:
                hex2.deselect()
                self.selectHex(hex1)
            else:
                hex1.deselect()
                self.selectHex(hex2)
        elif len(selected) == 1:
            self.selectHex(selected[0])
        elif len(selected) == 0 and self.selectedHex is not None:
            self.selectedHex.deselect()
            self.selectedHex = None
            self.action__move = False
            self.action__attack = False
            self.heldUnit = None

    def refreshTurnHexSprites(self):
        for hex in self.hexMap.values():
            if not hex.selected:
                hex.refreshHex()

    def setHex(self, row, col, isRoad, name, terrainType, terrainRoughness, initialFlag, switchedFlag=None,
               initialOwner=None):
        hex_key = f"{row},{col}"
        self.hexMap[hex_key].terrainType = terrainType
        self.hexMap[hex_key].terrainRoughness = terrainRoughness
        self.hexMap[hex_key].isRoad = isRoad
        self.hexMap[hex_key].name = name
        if initialFlag != "0":
            self.hexMap[hex_key].flag = Flag(self.batch, self.group, initialFlag, switchedFlag, initialOwner)

    def action(self, alreadyHeld):
        if self.selectedHex is not None:
            if alreadyHeld and alreadyHeld.unit is not None and alreadyHeld.unit.owner == 0:  # If unit was already selected
                # Moving
                if self.selectedHex.unit is None:
                    self.moveUnit(alreadyHeld, self.selectedHex)

                # actions for neighbour hexes
                if alreadyHeld.unit is None: return
                attackable_hexes = self.calculateSpot(alreadyHeld.row, alreadyHeld.col,
                                                      alreadyHeld.unit.baseAttackRange)
                if (self.selectedHex.row, self.selectedHex.col) in attackable_hexes:
                    # attacking
                    self.attack(alreadyHeld)

    def attack(self, alreadyHeld):
        if alreadyHeld.unit is None: return
        if alreadyHeld.unit.attack() is False: return
        if self.selectedHex.unit is not None and self.selectedHex.unit.owner != 0:
            responseInRange = False if (alreadyHeld.row, alreadyHeld.col) not in self.calculateSpot(
                self.selectedHex.row, self.selectedHex.col, self.selectedHex.unit.baseAttackRange) else True
            damage_given, damage_taken, ruggedDefense = calculateDamage(alreadyHeld.unit, self.selectedHex.unit,
                                                                        alreadyHeld, self.selectedHex)
            if responseInRange == False: damage_taken = 0
            self.currentOccurrence.text = 'attacking'
            self.currentOccurrence.x = alreadyHeld.x + 16
            self.currentOccurrence.y = alreadyHeld.y + 100
            self.borderLabel.text = 'attacking'
            self.borderLabel.x = alreadyHeld.x + 16 - 2
            self.borderLabel.y = alreadyHeld.y + 100 - 2
            if ruggedDefense is True:
                self.currentOccurrence.text = 'RUGGED DEFENSE!'
                self.currentOccurrence.color = RED
                self.currentOccurrence.x = self.selectedHex.x + 16
                self.currentOccurrence.y = self.selectedHex.y + 100
                self.borderLabel.text = 'RUGGED DEFENSE!'
                self.borderLabel.x = self.selectedHex.x + 16 - 1
                self.borderLabel.y = self.selectedHex.y + 100 - 1
            self.action__attack = True
            pyglet.clock.schedule_once(lambda dt: self.finish_attack(alreadyHeld, damage_given, damage_taken), 4)

    def finish_attack(self, alreadyHeld, damage_given, damage_taken):
        self.selectedHex.unit.hit(damage_given)
        alreadyHeld.unit.hit(damage_taken)
        self.currentOccurrence.text = ''
        self.currentOccurrence.color = YELLOW
        self.currentOccurrence.x = 0
        self.currentOccurrence.y = 0
        self.borderLabel.text = ''
        self.borderLabel.x = 0
        self.borderLabel.y = 0
        self.action__attack = False
        if damage_taken > 0: explosionAnimation1.startAtPos(alreadyHeld.x, alreadyHeld.y)
        if damage_given > 0: explosionAnimation2.startAtPos(self.selectedHex.unit.x, self.selectedHex.unit.y)
        if self.selectedHex.unit.destroyed is True:
            self.destroyUnit(self.selectedHex)
        if alreadyHeld.unit.destroyed is True:
            self.destroyUnit(alreadyHeld)

    def placeUnit(self, row, col, unit):
        hex_key = f"{row},{col}"
        self.hexMap[hex_key].unit = unit

    def placeOutUnit(self, row, col):
        hex_key = f"{row},{col}"
        self.hexMap[hex_key].unit = None

    def showVisibleHexes(self):
        self.showSpottedHexes()  # if non unit is selected
        self.showMovableHexes()  # if there is a unit selected
        self.showUnitsInRange()

    def calculateNeighbours(self, row, col):
        hexagons = set()
        hexagons.add((row, col))
        r, c = row, col
        dirs = [(1, 0), (0, 1), (-1, 0), (-1, -1), (1, -1), (1, 0)] if col % 2 == 1 else [(1, 0), (-1, 1), (-1, 0),
                                                                                          (0, -1), (0, -1), (1, 0)]
        for dr, dc in dirs:
            r, c = r + dr, c + dc
            hexagons.add((r, c))
        return hexagons

    def calculateSpot(self, row, col, bRange):
        hexagons = set()
        hexagons.add((row, col))
        for i in range(1, bRange + 1):
            new_hexagons = set()
            for hexagon in hexagons:
                neighbours = self.calculateNeighbours(hexagon[0], hexagon[1])
                for neighbour in neighbours:
                    if neighbour not in hexagons and neighbour not in new_hexagons:
                        new_hexagons.add(neighbour)
            hexagons.update(new_hexagons)
        return hexagons

    def calculateMoveRange(self, row, col, bRange):
        hexagons = set()
        hexagons.add((row, col))
        neighbours = self.calculateNeighbours(row, col)
        for neighbour in neighbours:
            if f"{neighbour[0]},{neighbour[1]}" not in self.hexMap: continue
            hex_roughness = self.hexMap[f"{neighbour[0]},{neighbour[1]}"].terrainRoughness
            if bRange >= hex_roughness:
                hexagons.add(neighbour)
                if bRange > hex_roughness:
                    hexagons.update(self.calculateMoveRange(neighbour[0], neighbour[1], bRange - hex_roughness))

        return hexagons

    def showUnitsInRange(self):
        if self.selectedHex is None or self.selectedHex.unit is None: return
        row = self.selectedHex.row
        col = self.selectedHex.col
        attackRange = self.selectedHex.unit.baseAttackRange
        if self.deploymentMode is True: return
        hexagons = self.calculateSpot(row, col, attackRange)
        for hexagon in hexagons:
            if f"{hexagon[0]},{hexagon[1]}" in  self.hexMap.values(): continue
            if self.hexMap[f"{hexagon[0]},{hexagon[1]}"].unit is not None:
                self.hexMap[f"{hexagon[0]},{hexagon[1]}"].isVisible = True


    def showSpottedHexes(self):
        if self.deploymentMode is True: return
        if self.selectedHex is None or self.selectedHex.unit is None or self.selectedHex.unit.owner != 0:
            for hex in self.hexMap.values():
                if DEBUG_MODE is True:
                    hex.isVisible = True
                    continue
                if hex.unit is not None and hex.unit.owner == 0:
                    visible = self.calculateSpot(hex.row, hex.col, hex.unit.baseSpotRange)
                    for v in visible:
                        hex_key = f"{v[0]},{v[1]}"
                        if hex_key in self.hexMap and self.hexMap[hex_key].isVisible is not True:
                            self.hexMap[hex_key].isVisible = True

    def showMovableHexes(self):
        if self.deploymentMode is True: return
        if self.selectedHex is not None and self.selectedHex.unit is not None and self.selectedHex.unit.owner == 0:
            row = self.selectedHex.row
            col = self.selectedHex.col
            unitRange = self.selectedHex.unit.baseMoveRange
            visible = self.calculateMoveRange(row, col, unitRange)
            for v in visible:
                hex_key = f"{v[0]},{v[1]}"
                if hex_key in self.hexMap and self.hexMap[hex_key].isVisible is not True:
                    self.hexMap[hex_key].isVisible = True

    def unspotAllHexes(self):
        for hex in self.hexMap.values():
            hex.isVisible = False

    def moveUnit(self, fromHex, toHex):
        unit = fromHex.unit
        if unit.owner == 0 and not unit.moved:
            fromHex.moveOutUnit()
            toHex.placeUnit(unit)
            self.action__move = False
            unit.moved = True

    def endTurn(self):
        for hex in self.hexMap.values():
            if hex.unit is not None:
                hex.unit.endTurn()

    def destroyUnit(self, hex):
        hex.unit = None

    def selectNextNotMovedUnit(self):
        for unit in self.players[0].units:
            if unit.moved is False:
                key = f"{unit.row},{unit.col}"
                hex = self.hexMap[key]
                self.selectHex(hex)
                self.centerOn(0,0,hex)
                break
        self.unspotAllHexes()
        self.showVisibleHexes()
        self.refreshTurnHexSprites()

    def getPossibleDeploymentHexes(self, player):
        deploymentHexes = set()
        for city_cords in self.players[player].cities:
            deploymentHexes.update(self.calculateNeighbours(city_cords[0], city_cords[1]))

        # now we need to check if any of the hexes are occupied
        for cords in deploymentHexes.copy():
            key = f'{cords[0]},{cords[1]}'
            if self.hexMap[key].unit is not None:
                deploymentHexes.remove(cords)

        return deploymentHexes

    def showDeployableHexes(self):
        if self.deploymentMode is True:
            deployableHexes = self.getPossibleDeploymentHexes(0)
            for cords in deployableHexes:
                key = f'{cords[0]},{cords[1]}'
                self.hexMap[key].isVisible = True

    def setDeploymentMode(self, unit):
        self.deploymentMode = True
        self.selectedHex = None
        self.heldUnit = unit
        self.unspotAllHexes()
        self.showDeployableHexes()
        self.refreshTurnHexSprites()

    def unsetDeploymentMode(self):
        if self.deploymentMode == True:
            self.deploymentMode = False
            self.selectedHex = None
            self.heldUnit = None

    def deployUnit(self, hex, unit):
        if self.deploymentMode is True:
            row = 0
            col = 0
            if hex is not None:
                row = hex.row
                col = hex.col
            unit.attacked = True
            unit.moved = True
            unit.row = row
            unit.col = col
            self.players[0].units.append(unit)
            self.placeUnit(row, col, unit)
            self.deploymentMode = False

    def centerOn(self, x, y, hex=None):
        # Determine the target position for the camera
        target_x = x if hex is None else hex.absX + hex.w/2
        target_y = y if hex is None else hex.absY + hex.h/2

        new_x = SCREEN_WIDTH / 2 - target_x
        new_y = SCREEN_HEIGHT / 2 - target_y

        current_x = self.map.x
        current_y = self.map.y
        if new_x > 0:
            new_x = 0
        if new_y > 0:
            new_y = 0
        if new_y < -(self.map.height - SCREEN_HEIGHT):
            new_y = -(self.map.height - SCREEN_HEIGHT)
        if new_x < -(self.map.width - SCREEN_WIDTH):
            new_x = -(self.map.width - SCREEN_WIDTH)

        self.map.y = new_y
        self.map.x = new_x

        for hex in self.hexMap.values():
            hex.x += (new_x - current_x)
            hex.y += (new_y - current_y)