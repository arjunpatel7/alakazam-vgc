import math
import random
import editdistance
import jsonlines


def poke_round(num):
    pass


def base_damage(base_power, attack, defense):
    # given args, calculatse base damage of attack

    LEVEL = 50

    level_weight = math.floor(((2 * LEVEL) / 5) + 2)

    step1 = math.floor((level_weight * base_power * attack) / defense)

    step2 = math.floor(step1 / 50) + 2

    return step2


# DaWoblefet calc exam[le]

# incin_calc = base_damage(base_power=70, attack=136, defense=100)
# print(incin_calc)
# assert incin_calc == 43, "Calc is wrong"


def spread_move_modifier(damage):
    # reduce damage by 0.75 and pokeround

    return poke_round(damage * (3072 / 4096))


def random_modifier(damage):
    n = random.randint(85, 100)

    return math.floor(damage * (100 - n) / 100)


def STAB_modifier(damage):
    return poke_round((6144 / 4096) * damage)


def burn_modifier(damage):
    pass


# BST to actual stat


def calc_stat(level, base, ev, iv, is_hp=False):
    first_term = math.floor((((2 * base) + iv + math.floor(ev / 4)) * level) / 100)
    if is_hp:
        return level + first_term + 10
    else:
        return math.floor(first_term + 5)


# quaxly_hp = calc_stat(50, 55, 252, 31, True)
# quaxly_atk = calc_stat(50, 65, 252, 31, False)

# print(quaxly_atk, quaxly_hp)
# assert quaxly_hp == 162, "HP calc is wrong"
# assert quaxly_atk == 117, "Atk calc is wrong"


# Attack stat modifirs


def stat_modifier(num_stages, stat):
    # given stat change, compute modifier and new stat
    modifier = 1
    direction = 1
    if num_stages <= 0:
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


#  gholdengo stat checks
# print("Gholdengo checks")
# ghol_test_1= stat_modifier(num_stages = 2, stat = calc_stat(50, 84, 252, 31))
# assert ghol_test_1 == 272, "Ghol test is wrong"

# ghol_test_2 = stat_modifier(num_stages = -3, stat = calc_stat(50, 84, 252, 31))
# print(ghol_test_2)
# assert ghol_test_2 == 54, "Ghol test is wrong"


# implement type effectivess checks
# figure out how to represent two pokemon and the resultant calculation


def read_in_pokemon(f):
    pokemons = []
    with jsonlines.open(f) as reader:
        for entry in reader:
            pokemons.append(entry)
    return pokemons


def lookup_pokemon(pokemon, pokemons):

    # first, check for exact match
    # if no exact match,check for edit distance closest

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


# print(lookup_pokemon("sprigatito")["name"])
# print(lookup_pokemon("samence")["name"])
# print(lookup_pokemon("fueco")["name"])


def type_check():
    # retrieve type modifier based on input types
    pass


def item_lookup():
    # return properties of item
    pass


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
    if p1_final_speed == p2_final_speed:
        return f"Speed Tie, with both pokemon at {p1_final_speed}"
    elif p1_final_speed < p2_final_speed:
        return f"{p1} speed stat is {p1_final_speed}, which is slower than {p2} at {p2_final_speed}"

    return f"{p1} speed stat is {p1_final_speed}, which is faster than {p2} at {p2_final_speed}"


def check_if_exists(d, arg):
    return d[arg] if arg in d.keys() else ""


# print(speed_check("gholdengho", "gholdengo", 2, -1, 252, 252))
# print(speed_check("gholdengho", "gholdengo", 2, 2, 252, 252))
# print(speed_check("gholdengho", "gholdengo", 2, 2, 252, 200))
# print(speed_check("flutter man", "iron bundle"))
# print(speed_check("flutter man", "iron bundle", p1_stat_changes=1))


def calculate_damage(p1, move, p2, p1_stat_changes, p2_stat_changes):
    # basic implementation of pokemon move calculator

    # lookup stats, type, of both pokemon

    # lookup move type and power
    # transform stats given stat changes
    # do damage calculation
    # factor in offensive/defensive items

    # return damage windows
    pass
