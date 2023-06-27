import streamlit as st
import random
import re
from supabase import create_client
import time
import modal
import ast
from calculations import (
    read_in_pokemon,
    speed_check,
    check_if_exists,
    speed_check_statement,
)
import pandas as pd

pokemons = read_in_pokemon("gen9_pokemon.jsonl")


if "convo_id" not in st.session_state:
    # create random convo id for each run of the application
    CONVO_ID = random.randint(100000, 999999)
    st.session_state.convo_id = CONVO_ID
if "session_history" not in st.session_state:
    st.session_state.session_history = []

# Supabase Setup
# set url and key from streamlit secrets
sb_url = st.secrets["SUPABASE_URL"]
sb_key = st.secrets["SUPABASE_KEY"]


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
    speed_check_calcs = speed_check(**speed_check_dict)

    speed_check_string, r = speed_check_statement(speed_check_calcs)

    return speed_check_string, speed_check_calcs, r


def get_speedcheck(prompt):

    # keep track of how long it takes to run
    start_time = time.time()

    # grab our PokemonSpeedCheck inference function from Modal and predict
    extract = modal.Function.lookup("pkmn-py", "run_inference")
    # call run_inference remotely on modal
    result = extract.call(prompt)
    st.write(result)
    speed_check_calcs = None
    # this is the string that will be the name of pokemon that is faster
    # write a better variable name for it
    r = None

    # Try to parse the result into the dictionary
    try:
        st.write("Calculating speed check...")
        speedcheck_outcome, speed_check_calcs, r = formatted_speed_check(
            result, pokemons
        )

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

    # add prompt and query result to session history
    # note to self: history should be easier to view, by having columns for who is actually faster, the actual speeds, parameters, etc
    if speed_check_calcs is not None:
        # add to session history a structured respresentation of the speed_check
        # must include query, the faster pokemon, the final speeds, the parameters, and the time to result
        history_entry = {
            "query": prompt,
            "faster_pokemon": r,
            "p1": speed_check_calcs["p1"],
            "p2": speed_check_calcs["p2"],
            "p1_final_speed": speed_check_calcs["p1_final_speed"],
            "p2_final_speed": speed_check_calcs["p2_final_speed"],
            "p1_stat_changes": speed_check_calcs["p1_stat_changes"],
            "p2_stat_changes": speed_check_calcs["p2_stat_changes"],
            "p1_ev": speed_check_calcs["p1_ev"],
            "p2_ev": speed_check_calcs["p2_ev"],
            "time_to_result": convo_log["time_to_result"],
        }
        st.session_state.session_history.append(history_entry)


st.title("Welcome to alakazam!")

with st.sidebar:
    # create a description of the speedcheck bot in really fancy text
    st.header("What is alakazam")
    st.write(
        "alakazam allows you to pass natural language queries about Pokemon speedchecks and it will return the speedcheck outcome for you!"
    )
    st.write(
        "Right now, alakazam only support queries that include info about the two pokemon involved, their evs, and their speed stat changes."
    )
    st.write(
        "alakazam is NOT like chatgpt, so please be sure to ask only about speedchecks including the above info"
    )

st.subheader("Query Examples")
with st.expander("Here are some examples of queries you can ask speedcheck bot:"):
    st.write("Is -5 35 Noibat slower than -5 19 Blissey")
    st.write("Will Finneon with 230 speed evs outspeed Meowth with 215 speed evs")
    st.write("Does max speed Salamence outspeed 248 Talonflame?")

st.subheader("Ask away!")
input_prompt = st.text_input(label="Write your query here")


# I want to give users the ability to add queries to a cache, then compute all queries at once
# Below is the streamlit code for this

# if st.button("Add to cache"):
#     st.session_state.cache.append(input_prompt)
#     st.write(st.session_state.cache)


if input_prompt != "":
    get_speedcheck(input_prompt)


if len(st.session_state.session_history) > 0:
    st.subheader("Session History")
    # instead of writing the session history, make a data frame and display it
    session_history_df = pd.DataFrame(st.session_state.session_history)
    # rearrange columns so query is last
    session_history_df = session_history_df[
        [
            "faster_pokemon",
            "p1",
            "p2",
            "p1_final_speed",
            "p2_final_speed",
            "p1_stat_changes",
            "p2_stat_changes",
            "p1_ev",
            "p2_ev",
            "time_to_result",
            "query",
        ]
    ]
    st.dataframe(session_history_df)
