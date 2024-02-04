from .calculations import GameState
from typing import Optional

# functions for the "train" functionality in our app

# Goal is to create functions that  takes in a game state statement
# and returns optimal EVs for 1hko for the attacking pokemon


def calculate_optimal_evs(game_state: GameState, criteria: Optional[str] = "1hko"):
    """
    Calculates optimal EVs for 1hko for the attacking pokemon
    """

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
          (and all possible p2 spreads, and boosting items)
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

    # adjust evs_remaining to account for the fact that we can't exceed 252+252+4 across stats
    evs_remaining = min(508 - sum(game_state.p1.evs.values()), 252)

    # determine the minimum damage required to 1hko or 2hko
    if criteria == "2hko":
        damage_min = round(game_state.p2.trained_stats["hp"] / 2)
    else:
        damage_min = game_state.p2.trained_stats["hp"]

    # Check if max 252 investment KOs
    min_damage, _ = game_state.calculate_modified_damage()
    if min_damage >= game_state.p2.stats["hp"]:
        results.append(
            {
                "evs_invested": evs_remaining,
                "stat": higher_stat_name,
                "training": "max",
                "criteria": criteria,
            }
        )

    while evs_remaining > 0:
        evs_remaining -= 4
        # calculate damage
        game_state.p1 = game_state.p1.retrain(stat=higher_stat_name, ev=evs_remaining)
        min_damage, _ = game_state.calculate_modified_damage()
        if min_damage < damage_min:
            print("Optimiality achieved")
            results.append(
                {
                    "evs_invested": evs_remaining + 4,
                    "stat": higher_stat_name,
                    "training": "optimal",
                    "criteria": criteria,
                }
            )
            break

    return results
