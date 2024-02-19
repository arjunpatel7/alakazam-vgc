import sys
import jsonlines
from langchain import PromptTemplate
import random
from random_properties import (
    random_mon,
    random_item,
    random_nature,
    random_tera_type,
    random_move,
    random_weather,
    random_criteria,
    random_written_spread,
)
from app.utils.parsing_json import json_to_gamestate
import json
from tqdm import tqdm

sys.path.insert(0, "/Users/ArjunPatel/Desktop/personal_projects/pkmn_calcs/pkmn_py/")


"""
In this section, we will define prompt templates for the nli model to train on
The model will accept a statement containing the following info:
- attacking pokemon (pokemon 1)
- defending pokemon (pokemon 2)
- move
- whether to check ohko or 2hko



The statement may also contain the following info:
- defending pokemon spread
- game state info (weather, terrain, etc)
- tera type (defensive or offensive)
- item (defensive or offensive)
- nature (defensive or offensive)

"""

# Takes about 11 minutes to run. Needs to be faster!!


# first section of prompts

simple_templates = [
    "train {p1} using {move} to {criteria} {p2}.",
    "Calculate the optimal evs for {p1} to {criteria} {p2} using {move}.",
    "What are the optimal evs for {p1} to {criteria} {p2} using {move}?",
]


spread_templates = [
    "Train {p1} using {move} to {criteria} {p2} with {p2_spread}.",
    "Calculate the optimal evs for {p1} to {criteria} {p2} using {move} with {p2_spread}.",
    "What are the optimal evs for {p1} to {criteria} {p2} using {move} with {p2_spread}?",
]

defensive_specified = [
    # these prompts will contain a defensive item, nature, or tera type
    # they may contain any number of these
    # all properties
    "Train {p1} using {move} to {criteria} {p2} with {p2_spread} holding {p2_item} with {p2_nature} nature and tera {p2_tera_type} active.",
    "Calculate the optimal evs {p1} using {move} to {criteria} {p2} with {p2_spread} holding {p2_item} with {p2_nature} nature and tera \
    {p2_tera_type} active.",
    "Train {p1} using {move} to {criteria} {p2} with {p2_nature} {p2_spread} holding {p2_item} with tera {p2_tera_type} active.",
]

defensive_item_specified = [
    "Train {p1} using {move} to {criteria} {p2} with {p2_spread} holding {p2_item}."
]

defensive_nature_specified = [
    "Train {p1} using {move} to {criteria} {p2} with {p2_spread} with {p2_nature} nature.",
]

defensive_tera_type_specified = [
    "Train {p1} using {move} to {criteria} {p2} with {p2_spread} with tera {p2_tera_type} active.",
]

offensive_specified = [
    # these prompts will contain an offensive item, nature, or tera type
    # same as defensive_specified, but with p1 instead of p2
    # all properties
    "Train {p1} with {p1_item} and {p1_nature} tera {p1_tera_type} active using {move} to {criteria} {p2} with {p2_spread} holding {p2_item} with \
          {p2_nature} nature and tera {p2_tera_type} active.",
    "Calculate the optimal evs for {p1} with {p1_item} and {p1_nature} tera {p1_tera_type} active using {move} to {criteria} {p2} with {p2_spread}\
          holding {p2_item} with {p2_nature} nature and tera {p2_tera_type} active.",
]

offensive_item_specified = [
    # one of each
    "Train {p1} with {p1_item} using {move} to {criteria} {p2}",
]

offensive_nature_specified = [
    "Train {p1} with {p1_nature} nature using {move} to {criteria} {p2}",
]

offensive_tera_type_specified = [
    "Train {p1} with tera {p1_tera_type} using {move} to {criteria} {p2}",
]


fully_specified = [
    # these prompts will contain both offensive and defensive items, natures, or tera types
    # in addition to spread, and game state extras
    # all properties
    "Train {p1} with {p1_item} and {p1_nature} tera {p1_tera_type} active using {move} to {criteria} {p2} with {p2_spread} holding {p2_item} with \
        {p2_nature} nature and tera {p2_tera_type} active in {weather}.",
    "Calculate the optimal evs for {p1} with {p1_item} and {p1_nature} tera {p1_tera_type} active using {move} to {criteria} {p2} with {p2_spread} \
          holding {p2_item} with {p2_nature} nature in {weather} with tera {p2_tera_type} active.",
    "Train {p1_nature} {p1} with {p1_item} and tera {p1_tera_type} active using {move} to {criteria} {p2_nature} {p2} with {p2_spread} holding \
        {p2_item} with tera {p2_tera_type} active in {weather}.",
]


# in each prompt, randomlly replace the "train" verb with "/train"
# this will allow the model to learn to recognize the command as a training prompt


def modify_train_verb(prompt, change_prob=0.5):
    i = random.random()
    if i > change_prob:
        prompt = prompt.replace("Train", "/train")
        return prompt
    return prompt


# Now, we'll define a function to construct a single example


def construct_simple_example():
    p1 = random_mon()
    p2 = random_mon()
    move = random_move()
    criteria = random_criteria()
    prompt = PromptTemplate.from_template(random.choice(simple_templates))
    prompt = prompt.format(p1=p1, p2=p2, move=move, criteria=criteria)

    # create corresponding arg string

    arg_string = f"""
    {{
        "p1": {{"name":"{p1}"}},
        "p2": {{"name":"{p2}"}},
        "move": {{"name":"{move}"}},
        "action": {{"name": "train", "args": {{"criteria": "{criteria}"}}}}
    }}
    """
    return {"prompt": modify_train_verb(prompt), "output": arg_string}


def construct_spread_example():
    p1 = random_mon()
    p2 = random_mon()
    move = random_move()
    criteria = random_criteria()
    written_spread, spread = random_written_spread()
    prompt = PromptTemplate.from_template(random.choice(spread_templates))
    prompt = prompt.format(
        p1=p1, p2=p2, move=move, criteria=criteria, p2_spread=written_spread
    )

    arg_string = f"""
    {{
        "p1": {{"name":"{p1}"}},
        "p2": {{"name":"{p2}", "evs": {json.dumps(spread)}}},
        "move": {{"name":"{move}"}},
        "action": {{"name": "train", "args": {{"criteria": "{criteria}"}}}}
    }}
    """
    return {"prompt": modify_train_verb(prompt), "output": arg_string}


def construct_defensive_specified_example():
    p1 = random_mon()
    p2 = random_mon()
    move = random_move()
    criteria = random_criteria()
    written_spread, spread = random_written_spread()
    item = random_item()
    nature = random_nature()
    tera_type = random_tera_type()
    prompt = PromptTemplate.from_template(random.choice(defensive_specified))
    prompt = prompt.format(
        p1=p1,
        p2=p2,
        move=move,
        criteria=criteria,
        p2_spread=written_spread,
        p2_item=item,
        p2_nature=nature,
        p2_tera_type=tera_type,
    )

    arg_string = f"""
    {{
        "p1": {{"name":"{p1}"}},
        "p2": {{"name":"{p2}", "evs": {json.dumps(spread)}, "item": "{item}", "nature": "{nature}", "tera_type": "{tera_type}"}},
        "move": {{"name":"{move}"}},
        "action": {{"name": "train", "args": {{"criteria": "{criteria}"}}}}
    }}
    """

    return {"prompt": modify_train_verb(prompt), "output": arg_string}


def construct_defensive_item_specified_example():
    p1 = random_mon()
    p2 = random_mon()
    move = random_move()
    criteria = random_criteria()
    written_spread, spread = random_written_spread()
    item = random_item()
    prompt = PromptTemplate.from_template(random.choice(defensive_item_specified))
    prompt = prompt.format(
        p1=p1,
        p2=p2,
        move=move,
        criteria=criteria,
        p2_spread=written_spread,
        p2_item=item,
    )

    arg_string = f"""
    {{
        "p1": {{"name":"{p1}"}},
        "p2": {{"name":"{p2}", "evs": {json.dumps(spread)}, "item": "{item}"}},
        "move": {{"name":"{move}"}},
        "action": {{"name": "train", "args": {{"criteria": "{criteria}"}}}}
    }}
    """
    return {"prompt": modify_train_verb(prompt), "output": arg_string}


def construct_defensive_nature_specified_example():
    p1 = random_mon()
    p2 = random_mon()
    move = random_move()
    criteria = random_criteria()
    nature = random_nature()
    written_spread, spread = random_written_spread()

    prompt = PromptTemplate.from_template(random.choice(defensive_nature_specified))
    prompt = prompt.format(
        p1=p1,
        p2=p2,
        move=move,
        criteria=criteria,
        p2_nature=nature,
        p2_spread=written_spread,
    )

    arg_string = f"""
    {{

        "p1": {{"name":"{p1}"}},
        "p2": {{"name":"{p2}", "nature": "{nature}", "evs": {json.dumps(spread)}}},
        "move": {{"name":"{move}"}},
        "action": {{"name": "train", "args": {{"criteria": "{criteria}"}}}}
    }}
    """
    return {"prompt": modify_train_verb(prompt), "output": arg_string}


def construct_defensive_tera_type_specified_example():
    p1 = random_mon()
    p2 = random_mon()
    move = random_move()
    criteria = random_criteria()
    written_spread, spread = random_written_spread()
    tera_type = random_tera_type()
    prompt = PromptTemplate.from_template(random.choice(defensive_tera_type_specified))
    prompt = prompt.format(
        p1=p1,
        p2=p2,
        move=move,
        criteria=criteria,
        p2_spread=written_spread,
        p2_tera_type=tera_type,
    )

    arg_string = f"""
    {{
        "p1": {{"name":"{p1}"}},
        "p2": {{"name":"{p2}", "evs": {json.dumps(spread)}, "tera_type": "{tera_type}"}},
        "move": {{"name":"{move}"}},
        "action": {{"name": "train", "args": {{"criteria": "{criteria}"}}}}
    }}
    """
    return {"prompt": modify_train_verb(prompt), "output": arg_string}


def construct_offensive_specified_example():
    p1 = random_mon()
    p2 = random_mon()
    move = random_move()
    criteria = random_criteria()
    item = random_item()
    nature = random_nature()
    tera_type = random_tera_type()
    written_spread, p2_spread = random_written_spread()
    p2_item = random_item()
    p2_nature = random_nature()
    p2_tera_type = random_tera_type()
    prompt = PromptTemplate.from_template(random.choice(offensive_specified))
    prompt = prompt.format(
        p1=p1,
        p2=p2,
        move=move,
        criteria=criteria,
        p1_item=item,
        p1_nature=nature,
        p1_tera_type=tera_type,
        p2_spread=written_spread,
        p2_item=p2_item,
        p2_nature=p2_nature,
        p2_tera_type=p2_tera_type,
    )

    arg_string = f"""
    {{
        "p1": {{"name":"{p1}", "item": "{item}", "nature": "{nature}", "tera_type": "{tera_type}"}},
        "p2": {{"name":"{p2}", "evs": {json.dumps(p2_spread)}, "item": "{p2_item}", "nature": "{p2_nature}", "tera_type": "{p2_tera_type}"}},
        "move": {{"name":"{move}"}},
        "action": {{"name": "train", "args": {{"criteria": "{criteria}"}}}}
    }}
    """
    return {"prompt": modify_train_verb(prompt), "output": arg_string}


def construct_offensive_item_specified_example():
    p1 = random_mon()
    p2 = random_mon()
    move = random_move()
    criteria = random_criteria()
    item = random_item()
    prompt = PromptTemplate.from_template(random.choice(offensive_item_specified))
    prompt = prompt.format(p1=p1, p2=p2, move=move, criteria=criteria, p1_item=item)

    arg_string = f"""
    {{
        "p1": {{"name":"{p1}", "item": "{item}"}},
        "p2": {{"name":"{p2}"}},
        "move": {{"name":"{move}"}},
        "action": {{"name": "train", "args": {{"criteria": "{criteria}"}}}}
    }}
    """
    return {"prompt": modify_train_verb(prompt), "output": arg_string}


def construct_offensive_nature_specified_example():
    p1 = random_mon()
    p2 = random_mon()
    move = random_move()
    criteria = random_criteria()
    nature = random_nature()
    prompt = PromptTemplate.from_template(random.choice(offensive_nature_specified))
    prompt = prompt.format(p1=p1, p2=p2, move=move, criteria=criteria, p1_nature=nature)

    arg_string = f"""
    {{

        "p1": {{"name":"{p1}", "nature": "{nature}"}},
        "p2": {{"name":"{p2}"}},
        "move": {{"name":"{move}"}},
        "action": {{"name": "train", "args": {{"criteria": "{criteria}"}}}}
    }}
    """
    return {"prompt": modify_train_verb(prompt), "output": arg_string}


def construct_offensive_tera_type_specified_example():
    p1 = random_mon()
    p2 = random_mon()
    move = random_move()
    criteria = random_criteria()
    tera_type = random_tera_type()
    prompt = PromptTemplate.from_template(random.choice(offensive_tera_type_specified))
    prompt = prompt.format(
        p1=p1, p2=p2, move=move, criteria=criteria, p1_tera_type=tera_type
    )

    arg_string = f"""
    {{
        "p1": {{"name":"{p1}", "tera_type": "{tera_type}"}},
        "p2": {{"name":"{p2}"}},
        "move": {{"name":"{move}"}},
        "action": {{"name": "train", "args": {{"criteria": "{criteria}"}}}}
    }}
    """
    return {"prompt": modify_train_verb(prompt), "output": arg_string}


def construct_fully_specified_example():
    p1 = random_mon()
    p2 = random_mon()
    move = random_move()
    criteria = random_criteria()
    written_defensive, defensive_spread = random_written_spread()

    offensive_item = random_item()
    defensive_item = random_item()

    offensive_nature = random_nature()
    defensive_nature = random_nature()

    offensive_tera_type = random_tera_type()
    defensive_tera_type = random_tera_type()

    weather = random_weather()
    prompt = PromptTemplate.from_template(random.choice(fully_specified))
    prompt = prompt.format(
        p1=p1,
        p2=p2,
        move=move,
        criteria=criteria,
        p1_item=offensive_item,
        p1_nature=offensive_nature,
        p1_tera_type=offensive_tera_type,
        p2_spread=written_defensive,
        p2_item=defensive_item,
        p2_nature=defensive_nature,
        p2_tera_type=defensive_tera_type,
        weather=weather,
    )

    arg_string = f"""
    {{
        "p1": {{"name":"{p1}", "item": "{offensive_item}", "nature": "{offensive_nature}", "tera_type": "{offensive_tera_type}"}},
        "p2": {{"name":"{p2}", "evs": {json.dumps(defensive_spread)}, "item": "{defensive_item}", "nature": "{defensive_nature}", \
            "tera_type": "{defensive_tera_type}"}},
        "move": {{"name":"{move}"}},
        "gamestate": {{"weather": "{weather}"}},
        "action": {{"name": "train", "args": {{"criteria": "{criteria}"}}}}
    }}
    """
    return {"prompt": modify_train_verb(prompt), "output": arg_string}


random.seed(1)


# Now, we can generate the entire dataset
def create_dataset(fp, NUM_EXAMPLES=5000):
    with jsonlines.open(fp, mode="w") as writer:
        # now, we generate 500 examples of each kind
        # shoutout github copilot for this fire code

        construct_functions = {
            construct_simple_example: NUM_EXAMPLES,
            construct_spread_example: NUM_EXAMPLES,
            construct_defensive_specified_example: NUM_EXAMPLES,
            construct_defensive_item_specified_example: NUM_EXAMPLES,
            construct_defensive_nature_specified_example: NUM_EXAMPLES,
            construct_defensive_tera_type_specified_example: NUM_EXAMPLES,
            construct_offensive_specified_example: NUM_EXAMPLES,
            construct_offensive_item_specified_example: NUM_EXAMPLES,
            construct_offensive_nature_specified_example: NUM_EXAMPLES,
            construct_offensive_tera_type_specified_example: NUM_EXAMPLES,
            construct_fully_specified_example: NUM_EXAMPLES,
        }

        stop = False
        for construct_func, loop_count in tqdm(
            construct_functions.items(), desc="Generating data"
        ):
            if stop:
                break
            for _ in tqdm(
                range(loop_count), desc=f"Generating data for {construct_func.__name__}"
            ):
                example = construct_func()
                # check that the example is valid
                # we'll load the arg string into the parsing functions and see if it throws an error
                json_to_gamestate(example["output"])
                writer.write(example)


create_dataset("train_action_training_data.jsonl", 5000)
create_dataset("train_action_eval_data.jsonl", 50)
