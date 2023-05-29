import jsonlines
from langchain import PromptTemplate
import random
import string


pokemons = []
with jsonlines.open("gen9_pokemon.jsonl") as reader:
    for entry in reader:
        pokemons.append(entry)


def random_ev():
    return random.randint(0, 252)


def random_stat_changes():
    stat_change = random.randint(-6, 6)
    if stat_change > 0:
        return "+" + str(stat_change)
    return str(stat_change)


def random_mon(pokemons):
    pokemon = random.choice(pokemons)["name"]
    pokemon = pokemon.replace("-", " ")
    pokemon = string.capwords(pokemon)
    return pokemon


templates = [
    "Does {p1_changes} {p1_ev} {p1} outspeed {p2_changes} {p2_ev} {p2}?",
    "Will {p1} at {p1_changes} with {p1_ev} outspeed {p2} at \
        {p2_changes} with {p2_ev}?",
    "Can you tell me if {p1} with {p1_ev} invested in speed \
        and {p1_changes} is faster than {p2} at {p2_changes} with {p2_ev} invested?",
    "Calculate if {p1} outspeeds {p2} where {p1} has {p1_ev} \
        invested in speed and at {p1_changes} and {p2} with \
            {p2_changes} changes and {p2_ev} speed evs invested?",
    "Check if {p1_changes} {p1_ev} {p1} outspeeds {p2_changes} {p2_ev} {p2}.",
    "Does {p1} with {p1_ev} speed evs at {p1_changes} \
        outspeed {p2} with {p2_ev} speed evs at {p2_changes}?",
    "Is {p1_changes} {p1_ev} {p1} slower than {p2_changes} {p2_ev} {p2}?",
    "Will {p1_changes} with {p1_ev} speed {p1} \
        underspeed {p2_changes} with {p2_ev} {p2}?",
]

max_speed = [
    "Does max speed {p1} outspeed max speed {p2}?",
    "Will max speed {p1} outspeed max speed {p2}?",
    "Can you tell me if max speed {p1} is faster than max speed {p2}?",
    "Calculate if max speed {p1} outspeeds max speed {p2}.",
    "Check if max speed {p1} outspeeds max speed {p2}.",
    "Does max speed {p1} outspeed max speed {p2}?",
    "Is max speed {p1} slower than max speed {p2}?",
    "Will max speed {p1} underspeed max speed {p2}?",
]

no_stat_changes = [
    "Does {p1} with {p1_ev} speed evs outspeed {p2} with {p2_ev} speed evs?",
    "Will {p1} with {p1_ev} speed evs outspeed {p2} with {p2_ev} speed evs?",
    "Can you tell me if {p1} with {p1_ev} speed evs is \
        faster than {p2} with {p2_ev} speed evs?",
    "Calculate if {p1} with {p1_ev} speed evs outspeeds {p2} with {p2_ev} speed evs.",
    "Check if {p1} with {p1_ev} speed evs outspeeds {p2} with {p2_ev} speed evs.",
    "Does {p1} with {p1_ev} speed evs outspeed {p2} with {p2_ev} speed evs?",
    "Is {p1} with {p1_ev} speed evs slower than {p2} with {p2_ev} speed evs?",
    "Will {p1} with {p1_ev} speed evs underspeed {p2} with {p2_ev} speed evs?",
]


def construct_example():

    p1 = random_mon(pokemons)
    p2 = random_mon(pokemons)
    p1_ev = random_ev()
    p2_ev = random_ev()
    p1_changes = random_stat_changes()
    p2_changes = random_stat_changes()

    # construct input prompt
    prompt = PromptTemplate.from_template(random.choice(templates))
    prompt = prompt.format(
        p1=p1,
        p2=p2,
        p1_ev=p1_ev,
        p2_ev=p2_ev,
        p1_changes=p1_changes,
        p2_changes=p2_changes,
    )
    # construct string for speed check

    arg_string = f"""
{{
    "p1": "{p1}",
    "p2": "{p2}",
    "p1_stat_changes": {int(p1_changes)},
    "p2_stat_changes": {int(p2_changes)},
    "p1_ev": {p1_ev},
    "p2_ev": {p2_ev}
}}
"""
    # return pair

    return {"prompt": prompt, "output": arg_string}


def construct_max_speed_example():
    # examples randomly sampled using the max_speed template
    p1 = random_mon(pokemons)
    p2 = random_mon(pokemons)

    # construct input prompt
    prompt = PromptTemplate.from_template(random.choice(max_speed))
    prompt = prompt.format(
        p1=p1,
        p2=p2,
    )
    # construct string for speed check

    arg_string = f"""
{{
    "p1": "{p1}",
    "p2": "{p2}",
    "p1_stat_changes": 0,
    "p2_stat_changes": 0,
    "p1_ev": 252,
    "p2_ev": 252
}}
"""

    # return pair
    return {"prompt": prompt, "output": arg_string}


def construct_no_stat_changes_examples():
    # create examples with no stat changes template
    p1 = random_mon(pokemons)
    p2 = random_mon(pokemons)
    p1_ev = random_ev()
    p2_ev = random_ev()

    # construct input prompt
    prompt = PromptTemplate.from_template(random.choice(no_stat_changes))
    prompt = prompt.format(p1=p1, p2=p2, p1_ev=p1_ev, p2_ev=p2_ev)
    # construct string for speed check

    arg_string = f"""
{{
    "p1": "{p1}",
    "p2": "{p2}",
    "p1_stat_changes": 0,
    "p2_stat_changes": 0,
    "p1_ev": {p1_ev},
    "p2_ev": {p2_ev}
}}
"""

    # return pair
    return {"prompt": prompt, "output": arg_string}


random.seed(1)

# need to wrap generation into a instruction and response

meta_prompt = """
Given the following input,
please parse it and return a valid JSON string
with the corresponding arguments.

Input: {input}
Output: {output}
"""


with jsonlines.open("speed_training_data.jsonl", mode="w") as writer:
    for x in range(0, 10000):
        example = construct_example()
        writer.write(example)
    for x in range(0, 5000):
        example = construct_max_speed_example()
        writer.write(example)
    for x in range(0, 5000):
        example = construct_no_stat_changes_examples()
        writer.write(example)

with jsonlines.open("speed_training_data_eval.jsonl", mode="w") as writer:
    for x in range(0, 100):
        example = construct_example()
        writer.write(example)
    for x in range(0, 50):
        example = construct_max_speed_example()
        writer.write(example)
    for x in range(0, 50):
        example = construct_no_stat_changes_examples()
        writer.write(example)
