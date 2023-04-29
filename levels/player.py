from levels.hex import Flag

class Player:
    def __init__(self, isAI):
        self.isAI = isAI
        self.units = []
        self.cities = set()
        self.flag = None

