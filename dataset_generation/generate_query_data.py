import random
from langchain.llms import Cohere

# This file will be exactly the same as generate_speed_data.py, except for the
# the prompts being related to the query task instead of the speed task.


def random_stat_name():
    return random.choice(
        ["attack", "defense", "special attack", "special defense", "speed"]
    )


# first section of prompts
# these simply ask the stat of a pokemon
stat_templates = [
    "What is the {stat} stat of {pokemon}?",
    "Tell me the {stat} of {pokemon}?",
    "{pokemon}'s {stat} stat is what value?",
    "What is {pokemon}'s {stat} stat?",
]

# second section of prompts
# these ask about the top X pokemon in a stat
top_x_templates = [
    "What are the top {x} pokemon in {stat}?"
    "Which pokemon are the top {x} in {stat} stat?"
]


# third section of prompts
# these ask about the bottom X pokemon in a stat

bottom_x_templates = [
    "What are the bottom {x} pokemon in {stat}?"
    "Who are the bottom {x} pokemon in {stat} stat?"
    "Which pokemon are the bottom {x} in {stat} stat?"
]


# fourth section of prompts
# these are random prompts that are unrelated to querying a pokemon's stats

# we'll use a Cohere generate endpoint to create the prompts and write them out


llm = Cohere(model="command")


def create_random_pokemon_prompts():
    for x in range(3):
        new_prompt = llm(
            "Come up with a one sentence statement related to the pokemon video game."
        )
        print(new_prompt)


create_random_pokemon_prompts()
