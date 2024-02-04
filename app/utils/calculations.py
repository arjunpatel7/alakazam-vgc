import math
import editdistance
import jsonlines
import ast
from typing import Dict, Optional
from app.utils.consts import offensive_type_resistance, offensive_type_effectiveness

# class based implementation of pokemon calculator
# TODO: Add in terrain modifications
# TODO: Add in nature modifications

MOVE_DATA_PATH = "./data/move_data.jsonl"


class Pokemon:
    # contains all relevant information about a pokemon

    def __init__(
        self,
        name: str,
        evs: Dict[str, int] = None,
        nature: Optional[str] = None,
        tera_type: Optional[str] = None,
        tera_active: Optional[bool] = False,
        status: Optional[str] = None,
        stat_stages: Optional[Dict[str, int]] = None,
        item: Optional[str] = None,
    ):
        self.name = name
        # evs is a dictionary mapping stat to ev
        self.evs = evs
        self.nature = nature
        self.tera_type = tera_type
        self.tera_active = tera_active
        self.status = status
        # also a dictionary, mapping stat to stat stage
        self.stat_stages = stat_stages
        self.item = item

        pokemon = lookup_pokemon(name, read_in_pokemon("./data/gen9_pokemon.jsonl"))
        # get types
        types = pokemon["types"]
        if isinstance(types, str):
            types = [types]
        self.types = types
        # get stats
        self.stats = {x["stat"]["name"]: x["base_stat"] for x in pokemon["stats"]}
        # upgrade stats based on evs
        self.trained_stats = create_trained_stats(self.evs, self.stats)

    def stat_stage_increase(self, stat: str, num_stages: int):
        # when a pokemon's stat increases, modify the stat and the stage_stages

        current_stages = self.stat_stages[stat]
        if current_stages is None:
            # if no stat stages, then just set it to 0
            current_stages[stat] = 0
        self.stat_stages[stat] = current_stages + num_stages
        self.trained_stats[stat] = stat_modifier(num_stages, self.trained_stats[stat])

    def retrain(self, stat: str, ev: int):
        # retrain a pokemon with new evs

        self.evs[stat] = ev
        # upgrade stats based on evs
        self.trained_stats[stat] = calc_stat(50, self.stats[stat], self.evs[stat], 31)
        return self

    def pretty_print(self):
        # prints out the pokemon name, and all stats, and attributes

        print(f"Pokemon is {self.name}")
        print(f"Pokemon types are {self.types}")
        print(f"Pokemon stats are {self.stats}")
        print(f"Pokemon evs are {self.evs}")
        print(f"Pokemon nature is {self.nature}")
        print(f"Pokemon tera type is {self.tera_type}")
        print(f"Pokemon tera active is {self.tera_active}")
        print(f"Pokemon status is {self.status}")
        print(f"Pokemon stat stages are {self.stat_stages}")

        # fill in stat distributions


class Move:
    # contains all relevant information about a move

    def __init__(
        self,
        name: Optional[str] = None,
        type: Optional[str] = None,
        category: Optional[str] = None,
        power: Optional[int] = None,
        priority: Optional[int] = 0,
        description: Optional[str] = None,
    ):
        self.name = name
        self.type = type
        self.category = category
        self.power = power
        self.priority = priority
        self.description = description

    @classmethod
    def from_name(cls, name: str):
        # given move name, return move
        moves = read_in_moves(MOVE_DATA_PATH)
        selected_move = None
        for move in moves:
            if move["name"] == name:
                selected_move = move
                break
        if selected_move is not None:
            move = Move(**selected_move)
        else:
            raise ValueError(f"Move {name} not found")


class GameState:
    # contains all relevant information about the game state

    def __init__(
        self,
        p1: Pokemon,
        p2: Pokemon,
        move: Move,
        weather: Optional[str] = None,
        terrain: Optional[str] = None,
        critical_hit: Optional[bool] = False,
    ):
        self.p1 = p1
        self.p2 = p2
        self.move = move
        self.weather = weather
        self.terrain = terrain
        self.critical_hit = False

    def calculate_base_damage(self):
        # given args, calculatse base damage of attack

        # lookup if move is physical or special

        category = self.move.category
        attacking_stat = "attack" if category == "physical" else "special-attack"
        defending_stat = "defense" if category == "physical" else "special-defense"

        # pull stat changes and stats from pokemon
        attacking_stat_changes = (
            0 if self.p1.stat_stages is None else self.p1.stat_stages[attacking_stat]
        )
        defending_stat_changes = (
            0 if self.p2.stat_stages is None else self.p2.stat_stages[defending_stat]
        )

        attacking_stat = stat_modifier(
            num_stages=attacking_stat_changes,
            stat=self.p1.trained_stats[attacking_stat],
        )
        defending_stat = stat_modifier(
            num_stages=defending_stat_changes,
            stat=self.p2.trained_stats[defending_stat],
        )

        LEVEL = 50

        level_weight = math.floor(((2 * LEVEL) / 5) + 2)

        # modify move base power based on item
        if self.p1.item is not None:
            self.move.power = bp_item_modifier(self.move, self.p1.item)

        step1 = math.floor(
            (level_weight * self.move.power * attacking_stat) / defending_stat
        )

        step2 = math.floor(step1 / 50) + 2

        return step2

    def calculate_modified_damage(self, verbose=False):
        base_damage = self.calculate_base_damage()
        verbose_print(verbose, message="Base damage of move is", result=base_damage)

        # spread move modifier
        final_damage = spread_move_modifier(base_damage)
        verbose_print(
            verbose, message="spread modified damage of move is", result=final_damage
        )

        # weather modifier
        final_damage = weather_modifier(self.weather, self.move.type, final_damage)
        verbose_print(
            verbose, message="weather modified damage of move is:", result=final_damage
        )

        # critical hit modifier
        final_damage = critical_hit_modifier(final_damage, self.critical_hit)
        verbose_print(
            verbose,
            message="critical hit modified damage of move is",
            result=final_damage,
        )
        # random modifier
        final_damage_min, final_damage_max = random_modifier(final_damage)
        verbose_print(verbose, message="random min of move is", result=final_damage_min)
        verbose_print(verbose, message="random max of move is", result=final_damage_max)

        # tera effectiveness modifier
        final_damage_min = tera_modifier(self.p1, self.move.type, final_damage_min)
        verbose_print(
            verbose, message="tera and stab effectiveness", result=final_damage_min
        )
        final_damage_max = tera_modifier(self.p1, self.move.type, final_damage_max)
        verbose_print(
            verbose, message="min damage after tera/stab mod", result=final_damage_min
        )

        verbose_print(
            verbose, message="max damage after tera/stab mod", result=final_damage_max
        )

        # type effectiveness modifier
        final_damage_min = type_modifier(final_damage_min, self)
        final_damage_max = type_modifier(final_damage_max, self)
        verbose_print(
            verbose,
            message="min damage after type effectiveness",
            result=final_damage_min,
        )
        verbose_print(
            verbose,
            message="max damage after type effectiveness",
            result=final_damage_max,
        )

        # burn modifier
        final_damage_min = burn_modifier(
            final_damage_min, self.move.category, self.p1.status
        )
        final_damage_max = burn_modifier(
            final_damage_max, self.move.category, self.p1.status
        )

        # final modifier/special cases

        return (final_damage_min, final_damage_max)


def verbose_print(verbose, result, message=""):
    if verbose:
        print(message, result)


def poke_round(num):
    # given a number, round it down if decimal is less than 0.5
    # round up if decimal is greater than 0.5

    decimal = num - math.floor(num)
    return math.floor(num) if decimal <= 0.5 else math.ceil(num)


def spread_move_modifier(damage, is_spread=False):
    # reduce damage by 0.75 and pokeround
    if is_spread:
        return poke_round(damage * (3072 / 4096))
    return damage


def read_in_moves(f):
    moves = []
    with jsonlines.open(f) as reader:
        for entry in reader:
            moves.append(entry)
    return moves


def lookup_move(move_name, move_data_path):

    # read in move data
    moves = read_in_moves(move_data_path)
    selected_move = None
    for move in moves:
        if move["name"] == move_name:
            selected_move = move
            break
    if selected_move is not None:
        move = Move(**selected_move)
    return None


def random_modifier(damage):
    # returns two values, which are the min and max damage possible

    return math.floor((damage * 85) / 100), poke_round(damage)


def STAB_modifier(damage):
    return poke_round((6144 / 4096) * damage)


def tera_modifier(pokemon, move_type, damage):
    # tera typing where the move is same type as pokemon
    # just doubles the stab modifier
    # otherwise if the types are different, we do a normal stab bonus
    pokemon_types = pokemon.types
    tera_type = pokemon.tera_type
    tera_active = pokemon.tera_active

    if tera_active:
        if tera_type == move_type:
            # then just do the 1.5x modifier
            if tera_type in pokemon_types:
                # then do the 2x modifier
                return poke_round((8192 / 4096) * damage)
            return STAB_modifier(damage)
    # then no modifier
    elif move_type in pokemon_types:
        return STAB_modifier(damage)
    else:
        return damage


def item_modifier(pokemon, item_class):
    if item_class in ["band", "banded", "choice band"]:
        # choice band ups attack by 1.5x
        pokemon.stat["attack"] = poke_round((6144 / 4096) * pokemon.stat["attack"])
    elif item_class in ["specs", "choice specs"]:
        # choice specs ups special attack by 1.5x
        pokemon.stat["special_attack"] = poke_round(
            (6144 / 4096) * pokemon.stat["special_attack"]
        )
    elif item_class in ["scarf", "choice scarf"]:
        # choice scarf ups speed by 1.5x
        pokemon.stat["speed"] = poke_round((6144 / 4096) * pokemon.stat["speed"])
    elif item_class in ["assault vest", "vest", "av"]:
        # assault vest ups special defense by 1.5x
        pokemon.stat["special_defense"] = poke_round(
            (6144 / 4096) * pokemon.stat["special_defense"]
        )
    return pokemon


def bp_item_modifier(move, item):
    # base power modifiers that occur with special items
    # for now, these are using placeholders to refer to classes of items
    if item == "boosted":
        # generic 1.2x boost
        return poke_round((12288 / 4096) * move.power)
    elif item == "life orb":
        # life orb 1.3x boost
        return poke_round((13312 / 4096) * move.power)
    return move.power


def weather_modifier(weather, move_type, damage):
    # account for sun or rain only
    # boosts for rain and water, and sun and fire
    # halves for rain and fire, and sun and water

    # does not do defense boost for hail or special
    # defense for sandstorm

    if weather == "rain" and move_type == "water":
        return poke_round((6144 / 4096) * damage)
    elif weather == "sun" and move_type == "fire":
        return poke_round((6144 / 4096) * damage)
    elif weather == "rain" and move_type == "fire":
        return poke_round((2048 / 4096) * damage)
    elif weather == "sun" and move_type == "water":
        return poke_round((2048 / 4096) * damage)
    else:
        return damage


def critical_hit_modifier(damage, critical_hit=False):
    # need to double check this one
    if critical_hit:
        return poke_round((6144 / 4096) * damage)
    return damage


# BST to actual stat


def calc_stat(level, base, ev, iv, is_hp=False):
    first_term = math.floor((((2 * base) + iv + math.floor(ev / 4)) * level) / 100)
    if is_hp:
        return level + first_term + 10
    else:
        return math.floor(first_term + 5)


# Attack stat modifirs


def stat_modifier(num_stages, stat):
    # given stat change, compute modifier and new stat
    modifier = 1
    direction = 1
    if num_stages == 0:
        return stat
    if num_stages < 0:
        direction = -1
        num_stages = abs(num_stages)
    if num_stages >= 6:
        modifier = 4
    elif num_stages == 5:
        modifier = 7 / 2
    elif num_stages == 4:
        modifier = 3
    elif num_stages == 3:
        modifier = 5 / 2
    elif num_stages == 2:
        modifier = 2
    elif num_stages == 1:
        modifier = 3 / 2

    if direction == -1:
        return math.floor((1 / modifier) * stat)
    return math.floor(modifier * stat)


def type_mulitplier_lookup(p2_type, move_type):
    # returns mulitplier for type effectiveness and resistance in a list
    is_resisted = p2_type in offensive_type_resistance[move_type]
    is_effective = p2_type in offensive_type_effectiveness[move_type]
    if is_resisted:
        return 0.5
    elif is_effective:
        return 2
    else:
        return 1


def type_multiplier(p2_type, move_type):
    # returns mulitplier for type effectiveness and resistance
    modifiers = [type_mulitplier_lookup(x, move_type) for x in p2_type]
    # good for if there is only one type
    return math.prod(modifiers)


def type_modifier(damage, gamestate):
    # grab types
    p2_type = gamestate.p2.types
    # grab types of move
    move_type = gamestate.move.type
    # override types if tera typing is active
    if gamestate.p2.tera_active:
        p2_type = [gamestate.p2.tera_type]

    # calculate type modifier
    return damage * type_multiplier(p2_type, move_type)

    # return type modifier


def burn_modifier(damage, category, status):
    # if pokemon is burned, and category is physical, then damage is halved
    if status == "burn" and category == "physical":
        return poke_round((2048 / 4096) * damage)
    return damage


def create_trained_stats(evs, stats):
    # given a pokemon's evs and stats, return trained stats
    # handles no-evs case by setting evs to 0
    ev_spread = evs.keys()
    trained_stats = {}
    for stat in stats:
        if stat == "hp":
            trained_stats[stat] = calc_stat(50, stats[stat], evs[stat], 31, is_hp=True)
        elif stat in ev_spread:
            trained_stats[stat] = calc_stat(50, stats[stat], evs[stat], 31)
        else:
            trained_stats[stat] = calc_stat(50, stats[stat], 0, 31)
    return trained_stats


def read_in_pokemon(f):
    pokemons = []
    with jsonlines.open(f) as reader:
        for entry in reader:
            pokemons.append(entry)
    return pokemons


def lookup_pokemon(pokemon, pokemons):
    # given pokemon name, return pokemon dict of stats

    # first, check for exact match
    # if no exact match,check for edit distance closest

    # preprocess pokemon names to avoid errors
    # check for whitespace, lowercase, commas, everything except hypens
    # and apostrophes

    # preprocess pokemon name
    pokemon = pokemon.replace(" ", "").replace(",", "").lower()

    all_pokemon = [x["name"] for x in pokemons]

    matched_pokemon = pokemon if pokemon in all_pokemon else None
    if matched_pokemon is None:
        # find the closest name by edit distance
        matched_pokemon = min(
            all_pokemon, key=lambda x: abs(editdistance.eval(pokemon, x))
        )
        # add a condition here that if the edit distance is too large
        # then we should return None
        if editdistance.eval(pokemon, matched_pokemon) > 4:
            return None

    # given pokemon dict, just grab relevant mon and return
    for poke in pokemons:
        if poke["name"] == matched_pokemon:
            return poke


# this function needs to be refactored to reflect changes in data_collection.py


def extract_stat(p, stat):
    return list(filter(lambda x: x["stat"]["name"] == stat, p["stats"]))[0]["base_stat"]


def speed_check(p1, p2, f, p1_stat_changes=0, p2_stat_changes=0, p1_ev=252, p2_ev=252):
    # given game state for changes, check if p1 stat outspeeds p2 stat

    pokemon_one = lookup_pokemon(p1.lower(), f)
    pokemon_two = lookup_pokemon(p2.lower(), f)

    # check if either pokemon is None
    # if so, return a failure message

    if pokemon_one is None:
        return f"{p1} is not a valid pokemon"
    if pokemon_two is None:
        return f"{p2} is not a valid pokemon"

    # from pokemon extract stat
    p1_speed = extract_stat(pokemon_one, "speed")
    p2_speed = extract_stat(pokemon_two, "speed")

    # we can now calculate speed stat after evs and ivs
    p1_final_speed = calc_stat(level=50, base=p1_speed, ev=p1_ev, iv=31)
    p2_final_speed = calc_stat(level=50, base=p2_speed, ev=p2_ev, iv=31)

    # now we can apply stat changes
    p1_final_speed = stat_modifier(num_stages=p1_stat_changes, stat=p1_final_speed)
    p2_final_speed = stat_modifier(num_stages=p2_stat_changes, stat=p2_final_speed)

    # we have all info to compare the two pokemon

    # return a dictionary with all function parameters AND the final speeds of each pokemon

    final_calculation = {
        "p1": pokemon_one["name"],
        "p2": pokemon_two["name"],
        "p1_final_speed": p1_final_speed,
        "p2_final_speed": p2_final_speed,
        "p1_stat_changes": p1_stat_changes,
        "p2_stat_changes": p2_stat_changes,
        "p1_ev": p1_ev,
        "p2_ev": p2_ev,
    }
    return final_calculation


def speed_check_statement(final_calculation):
    # given final calculation, return a statement the bot responds with
    p1 = final_calculation["p1"]
    p2 = final_calculation["p2"]
    p1_final_speed = final_calculation["p1_final_speed"]
    p2_final_speed = final_calculation["p2_final_speed"]

    if p1_final_speed == p2_final_speed:
        return f"Speed Tie, with both pokemon at {p1_final_speed}", "speed_tie"
    elif p1_final_speed < p2_final_speed:
        return (
            f"{p1} speed stat is {p1_final_speed}, which is slower than {p2} at {p2_final_speed}",
            p2,
        )

    return (
        f"{p1} speed stat is {p1_final_speed}, which is faster than {p2} at {p2_final_speed}",
        p1,
    )


def formatted_speed_check(arg_strings, f):
    # take arg_strings and format it into a dictionary for speed_check

    speed_check_dict = ast.literal_eval(arg_strings)

    p1 = check_if_exists(speed_check_dict, "p1")
    p2 = check_if_exists(speed_check_dict, "p2")
    p1_stat_changes = check_if_exists(speed_check_dict, "p1_stat_changes")
    p2_stat_changes = check_if_exists(speed_check_dict, "p2_stat_changes")
    p1_ev = check_if_exists(speed_check_dict, "p1_ev")
    p2_ev = check_if_exists(speed_check_dict, "p2_ev")
    print("Pokemons extracted successfully!")

    # wrap above variables into a dictionary, to pass to speed_check
    speed_check_dict = {
        "p1": p1,
        "p2": p2,
        "p1_stat_changes": p1_stat_changes,
        "p2_stat_changes": p2_stat_changes,
        "p1_ev": p1_ev,
        "p2_ev": p2_ev,
        "f": f,
    }

    # pass speed_check_dict to speed_check
    speed_check_calcs = speed_check(**speed_check_dict)

    speed_check_string, r = speed_check_statement(speed_check_calcs)

    return speed_check_string, speed_check_calcs, r


def check_if_exists(d, arg):
    return d[arg] if arg in d.keys() else ""
