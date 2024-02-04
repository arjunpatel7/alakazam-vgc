import pytest
from app.utils.train_pokemon import calculate_optimal_evs
from app.utils.calculations import Pokemon, Move, GameState
import pandas as pd

# This will will test the train_pokemon script

# Test a game state with a pokemon with 252 EVs in HP and the corresponding defensive stat


@pytest.fixture
def charizard():
    charizard_evs = {
        "hp": 0,
        "attack": 0,
        "defense": 0,
        "special-attack": 252,
        "special-defense": 0,
        "speed": 0,
    }
    return Pokemon("Charizard", charizard_evs, None)


@pytest.fixture
def eevee():
    eevee_evs = {
        "hp": 0,
        "attack": 0,
        "defense": 0,
        "special-attack": 0,
        "special-defense": 0,
        "speed": 0,
    }
    return Pokemon("Eevee", eevee_evs, None)


def test_optimal_ev_ohko(charizard, eevee):
    # test ohko
    move = Move("Overheat", "fire", "special", 130)
    practice_gamestate = GameState(charizard, eevee, move)
    results = pd.DataFrame(calculate_optimal_evs(practice_gamestate))
    assert results[results["training"] == "optimal"].evs_invested.iloc[0] == 172
