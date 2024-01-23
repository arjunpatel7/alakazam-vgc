from calculations import Pokemon, Move, GameState

# functions for the "train" functionality in our app

# Goal is to create functions that  takes in a game state statement
# and returns optimal EVs for 1hko for the attacking pokemon


def get_highest_base_power_move(pokemon: Pokemon):
    pass


def calculate_optimal_evs(game_state: GameState):
    """
    Calculates optimal EVs for 1hko for the attacking pokemon
    """

    # gamestate contains info about the ... entire game

    """
    1. Determine what the highest attacking stat of p1 is
    2. If move is not specified, find the highest base power move the pokemon can learn
    3. If p2 is not specified training-wise, assume three cases
        - p2 is a pokemon with 0 EVs
        - p2 is a pokemon with 252 EVs in HP
        - p2 is a pokemon with 252 EVs in HP and the corresping defensive stat

    4. if given move, move forward.
    5. Now, begin optimal EV calculation
        - for each possible condition in the following parameter sets:
          (neutral, super_effective, and all possible p2 spreads, and boosting items)
        - check if max ev in attacking stat is enough to 1hko p2
        - if enough, log this, and remove 4 EVs from attacking stat
        - repeat this process until 1hko is no longer possible
        - if never possible at max EVs, log this and move on
    6. Return optimal EVs for 1hko

    """

    results = []
    higher_stat_name = (
        "attack" if game_state.move.category == "physical" else "special-attack"
    )

    print("initial state")

    evs_remaining = 252

    # Check if max 252 investment KOs
    min_damage, _ = game_state.calculate_modified_damage()
    if min_damage >= game_state.p2.stats["hp"]:
        results.append(
            {"evs_invested": evs_remaining, "stat": higher_stat_name, "training": "max"}
        )

    while evs_remaining > 0:
        evs_remaining -= 4
        # calculate damage
        game_state.p1 = game_state.p1.retrain(stat=higher_stat_name, ev=evs_remaining)
        min_damage, _ = game_state.calculate_modified_damage()
        if min_damage < game_state.p2.trained_stats["hp"]:
            print("Optimiality achieved")
            results.append(
                {
                    "evs_invested": evs_remaining + 4,
                    "stat": higher_stat_name,
                    "training": "max",
                }
            )
            break

    return results


# Test a game state with a pokemon with 252 EVs in HP and the corresponding defensive stat


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


move = Move("Overheat", "fire", "special", 130)
practice_gamestate = GameState(charizard(), eevee(), move)
print(calculate_optimal_evs(practice_gamestate))
