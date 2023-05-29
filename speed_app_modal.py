import streamlit as st
import random
import re
from supabase import create_client
import time
import modal
import os
import ast
from calculations import read_in_pokemon, speed_check, check_if_exists


pokemons = read_in_pokemon("gen9_pokemon.jsonl")


if "convo_id" not in st.session_state:
    # create random convo id for each run of the application
    CONVO_ID = random.randint(100000, 999999)
    st.session_state.convo_id = CONVO_ID
    st.session_state.session_history = []

# Supabase Setup

sb_url = os.environ.get("SUPABASE_URL")
sb_key = os.environ.get("SUPABASE_KEY")


def search_json_dict(string):
    # thx chatgpt
    pattern = r"{.*?}"
    match = re.search(pattern, string)
    if match:
        json_dict_string = match.group()
        return json_dict_string
    else:
        return None


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
    speed_check_string = speed_check(**speed_check_dict)

    return speed_check_string, speed_check_dict


def get_speedcheck(prompt):

    # keep track of how long it takes to run
    start_time = time.time()

    # grab our PokemonSpeedCheck inference function from Modal and predict
    extract = modal.Function.lookup("pkmn-py", "run_inference")
    # call run_inference remotely on modal
    result = extract.call(prompt)
    st.write(result)
    # Try to parse the result into the dictionary
    try:
        st.write("Calculating speed check...")
        speedcheck_outcome, speed_check_dict = formatted_speed_check(result, pokemons)

        # Report the speed check outcome
        st.write(speedcheck_outcome)

        convo_log = {
            "query": prompt,
            "speed_check_string": result,
            "query_result": speedcheck_outcome,
            # speed_check_dict is causing timewritout error due to size
            # "speed_check_dict": speed_check_dict,
            "speed_check_pass": True,
            "convo_id": st.session_state.convo_id,
        }
        st.write("Speed check calculated successfully!")

    except SyntaxError:
        # save the error to supabase
        # leave other entires blank to be NULL
        convo_log = {
            "query": prompt,
            "speed_check_string": result,
            "speed_check_pass": False,
            "convo_id": st.session_state.convo_id,
        }
        st.write(
            """Sorry, I didn't understand that.
            Could you specify the pokemons, ev, and stat changes?
            """
        )
    # round time_to_result to 4 decimal places
    convo_log["time_to_result"] = round(time.time() - start_time, 4)
    st.write(convo_log["time_to_result"])
    supabase_client = create_client(sb_url, sb_key)
    supabase_client.table("speed-checks-logs").insert(convo_log).execute()


st.title("Welcome to speedcheck bot!")
input_prompt = st.text_input(label="Write your query here")

if input_prompt != "":
    get_speedcheck(input_prompt)
