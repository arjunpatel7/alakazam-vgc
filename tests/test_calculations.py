import pytest
from app.utils.calculations import calc_stat, stat_modifier, poke_round
from app.utils.calculations import read_in_pokemon
from app.utils.calculations import Pokemon, Move, GameState


def test_calc_stat_hp():
    quaxly_hp = calc_stat(50, 55, 252, 31, True)

    assert quaxly_hp == 162, "HP calc is wrong"


def test_calc_stat_atk():
    quaxly_atk = calc_stat(50, 65, 252, 31, False)

    assert quaxly_atk == 117, "Atk calc is wrong"


def test_stat_modifier_pos():

    #  gholdengo stat checks
    ghol_test_1 = stat_modifier(num_stages=2, stat=calc_stat(50, 84, 252, 31))
    assert ghol_test_1 == 272, "Ghol test is wrong"


def test_stat_modifier_neg():

    ghol_test_2 = stat_modifier(num_stages=-3, stat=calc_stat(50, 84, 252, 31))
    assert ghol_test_2 == 54, "Ghol test is wrong"


def test_poke_round():
    # classic test written in article from DeWoblefet on damage calculation

    assert poke_round(30.2) == 30, "poke_round is wrong"
    assert poke_round(30.5) == 30, "poke_round is wrong"
    assert poke_round(30.7) == 31, "poke_round is wrong"


# read in pokemon data as pytest fixture


@pytest.fixture
def pokemon_data():
    pokemons = read_in_pokemon("./data/gen9_pokemon.jsonl")
    return pokemons


@pytest.fixture
def fuecoco():
    fuecoco_evs = {
        "hp": 0,
        "attack": 252,
        "defense": 0,
        "special-attack": 0,
        "special-defense": 0,
        "speed": 252,
    }
    return Pokemon("Fuecoco", fuecoco_evs, None)


@pytest.fixture
def sprigatito():
    sprigatito_evs = {
        "hp": 0,
        "attack": 252,
        "defense": 0,
        "special-attack": 0,
        "special-defense": 0,
        "speed": 252,
    }
    return Pokemon("Sprigatito", sprigatito_evs, None)


@pytest.fixture
def charizard():
    charizard_evs = {
        "hp": 0,
        "attack": 252,
        "defense": 0,
        "special-attack": 252,
        "special-defense": 0,
        "speed": 0,
    }
    return Pokemon("Charizard", charizard_evs, None)


def test_calculate_base_damage_sprigatito(sprigatito, fuecoco):
    tackle = Move("Tackle", "normal", "physical", 40)
    game_state = GameState(sprigatito, fuecoco, tackle)
    base_damage_min, base_damage_max = game_state.calculate_modified_damage()

    # damage should be 22 min, 27 max
    assert (
        base_damage_min == 22 and base_damage_max == 27
    ), "Base damage calculation is wrong for Sprigatito"


def test_calculate_damage_sun_fire(charizard, sprigatito):

    fire_move = Move("Fire Blast", "fire", "special", 110)
    game_state = GameState(charizard, sprigatito, fire_move, weather="sun")

    base_damage_min, base_damage_max = game_state.calculate_modified_damage()

    assert (
        base_damage_min == 458 and base_damage_max == 542
    ), "Base damage calculation is wrong for Charizard in Sun with Fire Blast"


# write test for same scenario, but rain instead of sun
def test_calculate_base_damage_rain_fire(charizard, sprigatito):

    fire_move = Move("Fire Blast", "fire", "special", 110)
    game_state = GameState(charizard, sprigatito, fire_move, weather="rain")

    base_damage_min, base_damage_max = game_state.calculate_modified_damage()

    assert (
        base_damage_min == 152 and base_damage_max == 180
    ), "Base damage calculation is wrong for Charizard in Rain with Fire Blast"


def test_calculate_damage_fully_loaded(charizard, sprigatito):
    # mean to activate as many modifiers as possible

    fire_move = Move("Fire Blast", "fire", "special", 110)
    game_state = GameState(charizard, sprigatito, fire_move, weather="rain")

    # charizard modifiers
    charizard.stat_stages = {"special-attack": 2}
    charizard.tera_active = True
    charizard.tera_type = "fire"
    charizard.item = "specs"

    # sprigatito modifiers
    sprigatito.stat_stages = {"special-defense": 1}
    sprigatito.tera_active = True
    sprigatito.tera_type = "water"
    sprigatito.item = "av"

    base_damage_min, base_damage_max = game_state.calculate_modified_damage(
        verbose=True
    )

    assert (
        base_damage_min == 68 and base_damage_max == 81
    ), "Base damage calculation is wrong for Charizard in Rain with Fire Blast"


# Spread Moves


# Critical Hit
