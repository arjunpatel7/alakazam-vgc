import jsonlines
import random
import string
from app.utils.consts import natures, offensive_type_resistance
from app.utils.calculations import read_in_moves


pokemons = []
with jsonlines.open("./data/gen9_pokemon.jsonl") as reader:
    for entry in reader:
        pokemons.append(entry)

moves = read_in_moves("./data/move_data.jsonl")


def random_ev():
    return random.randint(0, 252)


def random_stat_changes():
    stat_change = random.randint(-6, 6)
    if stat_change > 0:
        return "+" + str(stat_change)
    return str(stat_change)


def random_mon():
    pokemon = random.choice(pokemons)["name"]
    pokemon = pokemon.replace("-", " ")
    pokemon = string.capwords(pokemon)
    return pokemon


def random_item():
    # returns a random boosting item
    items = [
        "life orb",
        "choice band",
        "choice specs",
        "av",
        "boosted",
        "banded",
        "specs",
        "assault vest",
    ]
    return random.choice(items)


def random_nature():
    # returns a random nature
    return random.choice(list(natures.keys()))
    pass


def random_tera_type():
    # returns a random tera type
    return random.choice(list(offensive_type_resistance.keys()))


def random_move():
    # returns a random move
    return random.choice(moves)["name"]


def random_weather():
    # returns a random weather
    weathers = ["rain", "sun"]
    return random.choice(weathers)


def random_spread():
    # returns a random spread, adhering to the 508 ev limit
    # also drops evs that would be allocated to 0
    total_evs = 508
    spread = {}

    while total_evs > 0:
        stat = random.choice(
            ["hp", "attack", "defense", "special-attack", "special-defense", "speed"]
        )
        ev = random_ev()

        if ev <= total_evs:
            spread[stat] = ev
            total_evs -= ev

    return spread


def random_written_spread():
    # returns a random spread which is written as if a VGC player would recite it
    spread = random_spread()
    # The rules are, you say "evs in stat and" for each stat,

    # if the evs are 0, you don't say anything
    # if the evs are 252, add a chance to say max stat instead of 252 stat

    # return the string, and the spread for argstring purpooses

    spread_string = ""
    for stat, ev in spread.items():
        if ev == 0:
            continue
        if ev == 252:
            # add a chance to say max stat instead of 252 stat
            max_chance = random.randint(0, 1)
            if max_chance == 1:
                spread_string += f"max {stat} and "
        else:
            spread_string += f"{ev} {stat} and "
    spread_string = spread_string[:-5]
    # add a chance to drop "and"
    # drop the last and if present
    and_chance = random.randint(0, 1)
    if and_chance == 1:
        spread_string = spread_string.replace("and", "", 1)

    return spread_string, spread


def random_criteria():
    criteria = ["1hko", "ohko", "2hko"]
    return random.choice(criteria)
