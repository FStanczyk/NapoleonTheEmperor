from levels.map import MAPS
from levels.unit import Unit
from levels.player import Player
from states.shop import SHOP
import xml.etree.ElementTree as ET
import pyglet
from pyglet import image
scale = 1.8
w = 64* scale
h = (64 - 6)* scale
from const import TERRAINS, TERRAINS_ROUGHNESS
class Level():

    def __init__(self, name, levelMap, file):
        self.map = levelMap
        self.name = name
        self.file = file
        self.batch = self.map.batch
        self.group = self.map.group
        self.players = [
            Player(False), # not AI (player)
            Player(True), # AI
        ]


    def initLevel(self):
        tree = ET.parse(self.file)
        unitsTree = ET.parse("units/units.xml")
        units = unitsTree.getroot()
        data = tree.getroot()
        hexes = data.find('hexes')
        units_map = data.find('units')
        objectives = data.find('objectives')
        start_balance = data.find('startBalance').text
        shopItems = data.find('shop')
        for hex in hexes.findall('Hex'):
            row = hex.get('row')
            col = hex.get('col')
            terrainType = TERRAINS[int(hex.get('terrainType'))]
            terrainRoughness = TERRAINS_ROUGHNESS[int(hex.get('terrainType'))]
            initialFlag = hex.get('initialFlag')
            switchedFlag = None
            initialOwner = None
            if initialFlag != "0":
                switchedFlag = hex.get('switchedFlag')
                initialOwner = int(hex.get('initialOwner'))
                self.players[initialOwner].cities.add((int(row), int(col)))
            isRoad = hex.get('isRoad')
            if isRoad == "True":
                print(isRoad)
                terrainRoughness = 1
            name = hex.get('name')
            self.map.setHex(row, col, isRoad, name, terrainType, terrainRoughness, initialFlag, switchedFlag, initialOwner)
            self.map.players = self.players

        for unit in units_map.findall('Unit'):

            id = unit.get('id')
            sample = units.find(f'''.//*[@id='{id}']''')
            texture = sample.get('texture')

            U = Unit(self.batch, self.group, texture)
            U.name = sample.get('name')
            U.nation = sample.get('nation')
            U.type = sample.get('type')
            U.experience = int(unit.get('experience'))
            U.baseMoveRange = int(sample.get('moveRange'))
            U.baseSpotRange = int(sample.get('spotRange'))
            U.strength = int(sample.get('strength'))
            U.unit_id = int(id)
            U.owner = int(unit.get('player'))
            U.row = int(unit.get('row'))
            U.col = int(unit.get('col'))
            row = unit.get('row')
            col = unit.get('col')

            if U.owner == 0:
                self.map.players[0].units.append(U)
            elif U.owner == 1:
                self.map.players[1].units.append(U)
            self.map.placeUnit(row, col, U)

        for objective in objectives:
            obj = {
                "type": objective.get('type'),
                "row": int(objective.get('row')),
                "col": int(objective.get('col')),
                "for_turns": int(objective.get('for_turns'))
            }
            self.map.objectives.append(obj)

        products = []
        for product in shopItems.findall('Unit'):
            id = product.get('id')
            sample = units.find(f'''.//*[@id='{id}']''')
            texture = sample.get('texture')
            U = Unit(self.batch, self.group, texture)
            U.name = sample.get('name')
            U.nation = sample.get('nation')
            U.type = sample.get('type')
            U.experience = int(product.get('experience'))
            U.price = int(product.get('price'))
            U.baseMoveRange = int(sample.get('moveRange'))
            U.baseSpotRange = int(sample.get('spotRange'))
            U.strength = int(sample.get('strength'))
            U.unit_id = int(id)
            U.owner = 0
            products.append(U)
        SHOP.initProducts(self.map, products, int(start_balance))

        self.map.players = self.players



LEVELS = {
    "Tutorial" :Level('Tutorial', MAPS["Tutorial"], "scenarios/tutorial.xml")
}