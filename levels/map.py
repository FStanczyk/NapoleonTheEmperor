import pyglet
from pyglet.window import mouse
from const import \
    MOVEABLE_WINDOW_W, MOVEABLE_WINDOW_H, \
    MOVE_MARGIN, MOVE_VELOCITY, \
    SCREEN_HEIGHT, SCREEN_WIDTH, \
    GUI_TOP, GUI_LEFT, GUI_RIGHT, GUI_BOTTOM
from levels.hex import Hex, Flag


W_LEFT_MOVE = MOVE_MARGIN
W_RIGHT_MOVE = SCREEN_WIDTH - MOVE_MARGIN
H_TOP_MOVE = SCREEN_HEIGHT - MOVE_MARGIN
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
        self.players = []
        rowsNeeded = int(image.height/ (64* 1.5)) + 1
        colsNeeded = int(image.width/64 * 0.75) + 2
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

        alreadyHeld = self.selectedHex


        if button & mouse.LEFT:
            self.calcSelectedHex(mouse_x, mouse_y)
        elif button & mouse.RIGHT:
            self.deselectHex()

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

    def setHex(self, row, col, isRoad, name, terrainType, terrainRoughness, initialFlag, switchedFlag=None, initialOwner=None):
        hex_key = f"{row},{col}"
        self.hexMap[hex_key].terrainType = terrainType
        self.hexMap[hex_key].terrainRoughness = terrainRoughness
        self.hexMap[hex_key].isRoad = isRoad
        self.hexMap[hex_key].name = name
        if initialFlag != "0":
            self.hexMap[hex_key].flag = Flag(self.batch, self.group, initialFlag, switchedFlag, initialOwner)

    def action(self, alreadyHeld):
        if self.selectedHex is not None:
            if alreadyHeld and alreadyHeld.unit is not None and alreadyHeld.unit.owner == 0: #If unit was already selected
                #Moving
                if self.selectedHex.unit is None:
                    self.moveUnit(alreadyHeld, self.selectedHex)

                # actions for neighbour hexes
                neighbour_hexes = self.calculateNeighbours(alreadyHeld.row, alreadyHeld.col)
                if (self.selectedHex.row, self.selectedHex.col) in neighbour_hexes:
                    # attacking
                    if self.selectedHex.unit is not None and self.selectedHex.unit.owner != 0:
                            damage = alreadyHeld.unit.attack()
                            self.selectedHex.unit.hit(damage)
                            if self.selectedHex.unit.destroyed is True:
                                self.destroyUnit(self.selectedHex)

    def placeUnit(self, row, col, unit):
        hex_key = f"{row},{col}"
        self.hexMap[hex_key].unit = unit

    def placeOutUnit(self, row, col):
        hex_key = f"{row},{col}"
        self.hexMap[hex_key].unit = None

    def showVisibleHexes(self):
        self.showSpottedHexes() # if non unit is selected
        self.showMovableHexes() # if there is a unit selected

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

    def calculateMoveRange(self, row, col, bRange):
        hexagons = set()
        hexagons.add((row, col))
        neighbours = self.calculateNeighbours(row, col)
        for neighbour in neighbours:
            hex_roughness= self.hexMap[f"{neighbour[0]},{neighbour[1]}"].terrainRoughness
            if bRange >= hex_roughness:
                hexagons.add(neighbour)
                if bRange > hex_roughness:
                    hexagons.update(self.calculateMoveRange(neighbour[0], neighbour[1], bRange - hex_roughness))

        return hexagons

    def showSpottedHexes(self):
        if self.deploymentMode is True: return
        if self.selectedHex is None or self.selectedHex.unit is None or self.selectedHex.unit.owner != 0:
            for hex in self.hexMap.values():
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
        print(self.players[0].units)

        for unit in self.players[0].units:
            print(unit.moved)
            if unit.moved is False:
                key = f"{unit.row},{unit.col}"
                hex = self.hexMap[key]
                self.selectHex(hex)
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

    def deployUnit(self, hex, unit):
        row = 0
        col = 0
        if hex is not None:
            row = hex.row
            col = hex.col
        if self.deploymentMode is True:
            unit.attacked = True
            unit.moved = True
            unit.row = row
            unit.col = col
            self.players[0].units.append(unit)
            self.placeUnit(row, col, unit)
            self.deploymentMode = False
MAPS = {
    "Tutorial": Map('graphics/maps/tutorial_map.jpg')
}