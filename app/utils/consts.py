# need to do all 18 types eventually.....
offensive_type_effectiveness = {
    # type maps to what types it is supereffective against
    "grass": ["water", "ground", "rock"],
    "fire": ["grass", "ice", "bug", "steel"],
    "water": ["fire", "ground", "rock"],
    "normal": ["nothing"],
    "electric": ["water", "flying"],
    "ice": ["grass", "ground", "flying", "dragon"],
    "fairy": ["fighting", "dragon", "dark"],
    "fighting": ["normal", "ice", "rock", "dark", "steel"],
    "poison": ["grass", "fairy"],
    "psychic": ["fighting", "poison"],
    "bug": ["grass", "psychic", "dark"],
    "dragon": ["dragon"],
    "ghost": ["psychic", "ghost"],
    "dark": ["psychic", "ghost"],
    "steel": ["ice", "rock", "fairy"],
    "flying": ["grass", "fighting", "bug"],
    "rock": ["fire", "ice", "flying", "bug"],
    "ground": ["fire", "electric", "poison", "rock", "steel"],
}

offensive_type_resistance = {
    # type maps to what types it is resisted by
    "grass": ["fire", "grass", "poison", "flying", "bug", "dragon", "steel"],
    "fire": ["fire", "water", "rock", "dragon"],
    "water": ["water", "grass", "dragon"],
    "normal": ["rock", "steel"],
    "electric": ["grass" "electric", "dragon"],
    "ice": ["steel", "fire", "water", "ice"],
    "fairy": ["fire", "poison", "steel"],
    "fighting": ["poison", "flying", "psychic", "bug", "fairy"],
    "poison": ["poison", "ground", "rock", "ghost"],
    "dragon": ["steel"],
    "psychic": ["psychic", "steel"],
    "bug": ["fire", "fighting", "poison", "flying", "ghost", "steel", "fairy"],
    "ghost": ["dark"],
    "dark": ["fighting", "dark", "fairy"],
    "steel": ["fire", "water", "electric", "steel"],
    "flying": ["electric", "rock", "steel"],
    "rock": ["fighting", "ground", "steel"],
    "ground": ["poison", "rock"],
}

natures = {
    # only natures that have actual VGC importance
    "adamant": {"attack": 1.1, "special-attack": 0.9},
    "modest": {"attack": 0.9, "special-attack": 1.1},
    "jolly": {"speed": 1.1, "special-attack": 0.9},
    "timid": {"speed": 1.1, "attack": 0.9},
    "brave": {"attack": 1.1, "speed": 0.9},
    "bold": {"defense": 1.1, "attack": 0.9},
    "impish": {"defense": 1.1, "special-attack": 0.9},
    "relaxed": {"defense": 1.1, "speed": 0.9},
    "quiet": {"special-attack": 1.1, "speed": 0.9},
    "calm": {"special-defense": 1.1, "attack": 0.9},
    "careful": {"special-defense": 1.1, "special-attack": 0.9},
    "sassy": {"special-defense": 1.1, "speed": 0.9},
    "naive": {"speed": 1.1, "special-defense": 0.9},
}
