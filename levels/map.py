import pyglet
from const import \
    MOVEABLE_WINDOW_W, MOVEABLE_WINDOW_H, \
    MOVE_MARGIN, MOVE_VELOCITY, \
    SCREEN_HEIGHT, SCREEN_WIDTH, \
    GUI_TOP, GUI_LEFT, GUI_RIGHT, GUI_BOTTOM
from levels.hex import Hex, Flag
from pyglet.window import mouse
W_LEFT_MOVE = MOVE_MARGIN
W_RIGHT_MOVE = GUI_RIGHT - MOVE_MARGIN
H_TOP_MOVE = GUI_TOP - MOVE_MARGIN
H_BOTTOM_MOVE = MOVE_MARGIN



class Map():
    def __init__(self, texturePath):
        image = pyglet.image.load(texturePath).get_texture()
        image.width *= 1.5
        image.height *= 1.5

        self.batch = pyglet.graphics.Batch()
        self.group = pyglet.graphics.Group()
        self.map = pyglet.sprite.Sprite(image, batch=self.batch)
        self.hexMap = {}

        rowsNeeded = int(image.height/ (64* 1.5)) + 1
        colsNeeded = int(image.width/64 * 0.75) + 2
        print(colsNeeded)
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

    def draw(self):
        self.batch.draw()
        for hex in self.hexMap.values():
            if hex.isVisible is True:
                hex.drawUnit()

    def moveMap(self, dir):
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

    def motion_update(self, mouse_x, mouse_y):
        self.overEdge = set()
        if mouse_x > W_RIGHT_MOVE and mouse_x < GUI_RIGHT:
            self.overEdge.add(2)
        if mouse_x < W_LEFT_MOVE and mouse_x > GUI_LEFT:
            self.overEdge.add(1)
        if mouse_y < H_BOTTOM_MOVE and mouse_y > GUI_BOTTOM:
            self.overEdge.add(3)
        if mouse_y > H_TOP_MOVE and mouse_y < GUI_TOP:
            self.overEdge.add(4)

    def press_update(self, mouse_x, mouse_y):
        pass

    def release_update(self, mouse_x, mouse_y, button):
        alreadyHeld = self.selectedHex

        if button & mouse.LEFT:
            self.calcSelectedHex(mouse_x, mouse_y)
        elif button & mouse.RIGHT:
            self.selectedHex.deselect()
            self.selectedHex = None
            self.action__move = False
            self.action__attack = False
            self.heldUnit = None

        if self.selectedHex is not None:
            #Select unit
            if self.selectedHex.unit is not None:
                self.action__move = True
                self.heldUnit = self.selectedHex.unit

            if alreadyHeld and alreadyHeld.unit is not None: #If unit was already selected
                #Moving
                if self.selectedHex.unit is None:
                    self.moveUnit(alreadyHeld, self.selectedHex)
                #attacking
                if self.selectedHex.unit is not None and self.selectedHex.unit.owner != 0:
                        damage = alreadyHeld.unit.attack()
                        self.selectedHex.unit.hit(damage)
                        if self.selectedHex.unit.destroyed is True:
                            self.destroyUnit(self.selectedHex)

        self.unspotAllHexes()
        self.showSpottedHexes()
        self.refreshTurnHexSprites()


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
                self.selectedHex = hex1
            else:
                hex1.deselect()
                self.selectedHex = hex2
        elif len(selected) == 1:
            self.selectedHex = selected[0]
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

    def setHex(self, row, col, terrainType, flag, isRoad, name):
        hex_key = f"{row},{col}"
        self.hexMap[hex_key].terrainType = terrainType
        self.hexMap[hex_key].isRoad = isRoad
        self.hexMap[hex_key].name = name
        if flag is not "0":
            f = Flag(self.batch, self.group, flag)
            self.hexMap[hex_key].flag = f

    def placeUnit(self, row, col, unit):
        hex_key = f"{row},{col}"
        self.hexMap[hex_key].unit = unit

    def placeOutUnit(self, row, col):
        hex_key = f"{row},{col}"
        self.hexMap[hex_key].unit = None


    def showSpottedHexes(self):
        if  self.selectedHex is None or self.selectedHex.unit is None or self.selectedHex.unit.owner != 0:
            for hex in self.hexMap.values():
                if hex.unit is not None and hex.unit.owner == 0:
                    visible = self.calculateSpot(hex.row, hex.col, hex.unit.baseMoveRange)
                    for v in visible:
                        hex_key = f"{v[0]},{v[1]}"
                        if hex_key in self.hexMap and self.hexMap[hex_key].isVisible is not True:
                            self.hexMap[hex_key].isVisible = True
        elif self.selectedHex is not None and self.selectedHex.unit is not None and self.selectedHex.unit.owner == 0:
            row = self.selectedHex.row
            col = self.selectedHex.col
            unitRange = self.selectedHex.unit.baseMoveRange
            visible = self.calculateSpot(row, col, unitRange)
            for v in visible:
                hex_key = f"{v[0]},{v[1]}"
                if hex_key in self.hexMap and self.hexMap[hex_key].isVisible is not True:
                    self.hexMap[hex_key].isVisible = True

    def calculateNeighbours(self, row, col):
        hexagons = set()
        hexagons.add((row, col))
        r, c = row, col
        dirs = [(1, 0), (0, 1), (-1, 0), (-1, -1), (1, -1), (1, 0)] if col % 2 == 1 else [(1, 0), (-1, 1), (-1, 0), (0, -1), (0, -1), (1, 0)]
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


MAPS = {
    "Tutorial": Map('graphics/maps/tutorial_map.jpg')
}