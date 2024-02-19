from app.utils.train_pokemon import calculate_optimal_evs
from app.utils.calculations import GameState, Pokemon, Move
import json

"""Contains code to parse JSON into gamestate and action objects"""
# checks I need to add:
# check if json is valid using json schema
# ensure that code doesn't break if game state is not in the json, it's possible to not have initalized a game state with special conditions
# ensure that code doesn't break if action is not in the json, it's possible to not have initalized any action


# should I need tests for json stuff if I check schema?


def json_to_gamestate(j):
    # given json, return gamestate object
    # We assume the JSON has keys for p1, p2, move, and gamestate arguments
    j = json.loads(j)

    pokemon_one = Pokemon(**j["p1"])
    pokemon_two = Pokemon(**j["p2"])

    move = Move.from_name(**j["move"])
    # check if gamestate is in the json
    if "gamestate" not in j:
        return GameState(pokemon_one, pokemon_two, move)
    gamestate = GameState(pokemon_one, pokemon_two, move, **j["gamestate"])
    return gamestate


def json_to_action(j):
    # Given a json, return the appropriate action's results
    # retrieve gamestate from json
    gamestate = json_to_gamestate(j)
    # based on action attribute in json, return the appropriate action

    # train
    action_results = ""
    if json["action"]["name"] == "train":
        # calculate optimal evs for 1hko
        # args so that we can use the same function for all actions
        action_results = calculate_optimal_evs(
            gamestate, json["action"]["args"]["criteria"]
        )

    # other actions that are not avail yet...

    return action_results
