from const import TERRAINS
import random
import math
attacker_multiplier = 1.0
defender_multiplier = 0.75
rugged_defense_cut = 3
rugged_defense_boost = 1.5
rugged_defense_chance_base = 0.15
rugged_defense_chance_city = 0.20
rugged_defense_chance_objective = 0.25
terrain_boost = [
    # defending\/
    # 0    1    2    3    4    5    6    7    8    9        - attacking \/
    [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0], # 0 - field
    [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0], # 1 - forest
    [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0], # 2 - mountain
    [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0], # 3 - beach
    [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0], # 4 - sea
    [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0], # 5 - river
    [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0], # 6 - river_bridge
    [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0], # 7 - city
    [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0], # 8 - desert
    [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]  # 9 - swamp
]

def calculateDamage(attackingUnit, defendingUnit, attackingHex, defendingHex):
    experience_difference = attackingUnit.experience - defendingUnit.experience
    hp_difference = attackingUnit.hp - defendingUnit.hp
    att_terrain = getTerrainKey(attackingHex.terrainType)
    def_terrain = getTerrainKey(defendingHex.terrainType)
    terrain_advantage_attacker = terrain_boost[att_terrain][def_terrain]
    terrain_advantage_defender = terrain_boost[def_terrain][att_terrain]
    att = attackingUnit.strength * attacker_multiplier
    dfn = defendingUnit.strength * defender_multiplier
    exp_att_boost = experience_difference/10 if experience_difference > 0 else -(experience_difference/10)
    exp_def_boost = experience_difference/10 if experience_difference < 0 else -(experience_difference/10)
    hp_att_boost = hp_difference/10  if hp_difference > 0 else -(hp_difference/10)
    hp_def_boost = hp_difference/10  if hp_difference < 0 else -(hp_difference/10)
    damage_given = ((att + att * exp_att_boost) * terrain_advantage_attacker)
    damage_taken = ((dfn + dfn * exp_def_boost) * terrain_advantage_defender)
    damage_given += damage_given * hp_att_boost
    damage_taken += damage_taken * hp_def_boost
    rugged_defence_p = rugged_defense_chance_city if defendingHex.flag is not None else rugged_defense_chance_base
    RUGGED_DEFENSE = randomP(rugged_defence_p)
    if RUGGED_DEFENSE is True:
        damage_given = damage_taken / rugged_defense_cut
        damage_taken = damage_taken * rugged_defense_boost
    return math.floor(damage_given), math.ceil(damage_taken), RUGGED_DEFENSE


def getTerrainKey(name):
    for key, value in TERRAINS.items():
        if value == name:
            return key
    return None
def randomP(p):
    if random.random() > p:
        return False
    else:
        return True