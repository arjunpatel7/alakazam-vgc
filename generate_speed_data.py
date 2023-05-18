import jsonlines
import json
from langchain import PromptTemplate

pokemons = []
with jsonlines.open("gen9_pokemon.jsonl") as reader:
    for entry in reader:
        pokemons.append(entry)


# generate different sentences that contain pokemon, stat changes, etc



import ast
import random
import string
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
    "Will {p1} at {p1_changes} with {p1_ev} outspeed {p2} at {p2_changes} with {p2_ev}?",
    "Can you tell me if {p1} with {p1_ev} invested in speed and {p1_changes} is faster than {p2} at {p2_changes} with {p2_ev} invested?",
    "Calculate if {p1} outspeeds {p2} where {p1} has {p1_ev} invested in speed and at {p1_changes} and {p2} with {p2_changes} changes and {p2_ev} speed evs invested?",
    "Check if {p1_changes} {p1_ev} {p1} outspeeds {p2_changes} {p2_ev} {p2}.",
    "Does {p1} with {p1_ev} speed evs at {p1_changes} outspeed {p2} with {p2_ev} speed evs at {p2_changes}?",
    "Is {p1_changes} {p1_ev} {p1} slower than {p2_changes} {p2_ev} {p2}?",
    "Will {p1_changes} with {p1_ev} speed {p1} underspeed {p2_changes} with {p2_ev} {p2}?"
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
        p1_ev = p1_ev, 
        p2_ev = p2_ev, 
        p1_changes = p1_changes, 
        p2_changes = p2_changes
    )
    # construct string for speed check

    arg_string = f'''
{{
    "p1": "{p1}",
    "p2": "{p2}",
    "p1_stat_changes": {int(p1_changes)},
    "p2_stat_changes": {int(p2_changes)},
    "p1_ev": {p1_ev},
    "p2_ev": {p2_ev}
}}
'''
    # return pair

    #print(arg_string)
    #print(ast.literal_eval(arg_string))
    #print(prompt)
    return {"prompt": prompt, "output": arg_string}

random.seed(1)

# need to wrap generation into a instruction and response

meta_prompt = '''
Given the following input, please parse it and return a valid JSON string with the corresponding arguments.

Input: {input}
Output: {output} 
'''
#with jsonlines.open('speed_training_data.jsonl', mode='w') as writer:
#    for x in range(0, 10000):
#        example = construct_example()
 #       writer.write(example)

print(construct_example())

#notes:

# shuffle dataset
# explore quantization to reduce model size
# explore using smaller model and different layers for PEFT
# use "max speed" phrasing
# include a nature check