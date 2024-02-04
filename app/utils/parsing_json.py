from train_pokemon import calculate_optimal_evs
from calculations import GameState, Pokemon, Move

"""Contains code to parse JSON into gamestate and action objects"""


def json_to_gamestate(json):
    # given json, return gamestate object
    # We assume the JSON has keys for p1, p2, move, and gamestate arguments

    pokemon_one = Pokemon(**json["p1"])
    pokemon_two = Pokemon(**json["p2"])

    move = Move.from_name(**json["move"])
    gamestate = GameState(pokemon_one, pokemon_two, move, **json["gamestate"])
    return gamestate


def json_to_action(json):
    # Given a json, return the appropriate action's results
    # retrieve gamestate from json
    gamestate = json_to_gamestate(json)
    # based on action attribute in json, return the appropriate action

    # train
    action_results = ""
    if json["action"]["name"] == "train":
        # calculate optimal evs for 1hko
        action_results = calculate_optimal_evs(gamestate, json["action"]["criteria"])

    # other actions that are not avail yet...

    return action_results
