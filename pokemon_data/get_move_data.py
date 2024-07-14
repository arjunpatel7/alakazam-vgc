# This script will retrieve move data from the PokeAPI and store it in a JSONL file
import requests
from tqdm import tqdm
import jsonlines
import backoff

moves_url = "https://pokeapi.co/api/v2/move?limit=100000&offset=0"


# Make request to pokeapi for all moves


# drop all moves that do not have a base power. For now, we will ignore spcail move cases

# then, write out moves to jsonl file with the following fields
# name, type, category, base_power, priority,


@backoff.on_exception(
    backoff.expo,
    requests.exceptions.RequestException,
    max_tries=8,
    giveup=lambda e: e.response is not None and e.response.status_code < 500,
)
def get_moves():
    moves = requests.get(moves_url)
    moves = moves.json()["results"]
    # this yields a list of dictionaries that have names and urls
    requested_moves = []

    for move in tqdm(moves):
        # request the move data
        try:
            move_data = requests.get(move["url"])
            move_data = move_data.json()
            # we need to get the name, type, category, base_power, priority
            move_info = {
                "name": move_data["name"],
                "type": move_data["type"]["name"],
                "category": move_data["damage_class"]["name"],
                "power": move_data["power"],
                "priority": move_data["priority"],
            }
            try:
                description = move_data["flavor_text_entries"][0]["flavor_text"]
            except Exception as e:
                print(move_info["name"])
                print(move_data["flavor_text_entries"])
                print(e)
                description = "Couldn't find it"

            move_info["description"] = description

            requested_moves.append(move_info)
        except Exception as e:
            print(e)
            print(move)
    return requested_moves


# combining everything together and writing it out
def write_all_moves(moves):
    with jsonlines.open("./data/move_data.jsonl", mode="w") as w:
        w.write_all(moves)
    return


moves = get_moves()
write_all_moves(moves)
