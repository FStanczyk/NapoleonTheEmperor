from levels.map import MAPS
from levels.unit import Unit
import xml.etree.ElementTree as ET
import pyglet
from const import TERRAINS
class Level():

    def __init__(self, name, levelMap, file):
        self.map = levelMap
        self.name = name
        self.file = file
        self.batch = self.map.batch
        self.group = self.map.group

    def initLevel(self):
        tree = ET.parse(self.file)
        unitsTree = ET.parse("units/units.xml")
        units = unitsTree.getroot()
        data = tree.getroot()
        hexes = data.find('hexes')
        units_map = data.find('units')
        for hex in hexes.findall('Hex'):
            row = hex.get('row')
            col = hex.get('col')
            terrainType = TERRAINS[int(hex.get('terrainType'))]
            flag = hex.get('flag')
            isRoad = hex.get('isRoad')
            name = hex.get('name')
            self.map.setHex(row, col, terrainType, flag, isRoad, name)

        for unit in units_map.findall('Unit'):

            id = unit.get('id')
            sample = units.find(f'''.//*[@id='{id}']''')
            texture = sample.get('texture')

            U = Unit(self.batch, self.group, texture)
            U.name = sample.get('name')
            U.nation = sample.get('nation')
            U.type = sample.get('type')
            U.baseMoveRange = int(sample.get('moveRange'))
            U.strength = int(sample.get('strength'))
            U.unit_id = int(id)
            U.owner = int(unit.get('player'))

            row = unit.get('row')
            col = unit.get('col')
            self.map.placeUnit(row, col, U)



LEVELS = {
    "Tutorial" :Level('Tutorial', MAPS["Tutorial"], "scenarios/tutorial.xml")
}