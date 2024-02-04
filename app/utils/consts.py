# need to do all 18 types eventually.....
offensive_type_effectiveness = {
    # type maps to what types it is supereffective against
    "grass": ["water", "ground", "rock"],
    "fire": ["grass", "ice", "bug", "steel"],
    "water": ["fire", "ground", "rock"],
    "normal": ["nothing"],
}

offensive_type_resistance = {
    # type maps to what types it is resisted by
    "grass": ["fire", "grass", "poison", "flying", "bug", "dragon", "steel"],
    "fire": ["fire", "water", "rock", "dragon"],
    "water": ["water", "grass", "dragon"],
    "normal": ["rock", "steel"],
}
