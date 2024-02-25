import streamlit as st
import random
import pandas as pd
from supabase import create_client
import time
import modal
from utils.calculations import read_in_pokemon, formatted_speed_check
from utils.base_stat_chat import handle_query, classify_intent
from utils.parsing_json import json_to_action

pokemons = read_in_pokemon("./data/gen9_pokemon.jsonl")

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


def get_speedcheck(prompt):
    # keep track of how long it takes to run
    start_time = time.time()
    # grab our PokemonSpeedCheck inference function from Modal and predict
    extract = modal.Function.lookup("pkmn-py", "run_inference")
    # call run_inference remotely on modal
    result = extract.remote(prompt)
    st.write(result)
    speed_check_calcs = None
    # this is the string that will be the name of pokemon that is faster
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


def get_train_calc(prompt):
    # Given a prompt corresponding to optimal ev calculation, parse it and run the inference back

    # keep track of how long it takes to run
    start_time = time.time()
    # grab our PokemonSpeedCheck inference function from Modal and predict
    extract = modal.Function.lookup("pkmn-dmg", "run_inference")
    # call run_inference remotely on modal
    result = extract.remote(prompt)
    st.write(result)
    try:
        # try to parse the result into json, and then the calc
        action_result = json_to_action(result)
        st.write(action_result)
        end_time = time.time()
        time_to_result = end_time - start_time
        st.write("Total time to result: ", time_to_result)
    except SyntaxError:
        st.write("Something went wrong, we couldn't parse this calculation")


st.title("Welcome to alakazam!")

github_url = "https://github.com/arjunpatel7/alakazam-vgc/"

github_star_button = """
    <iframe src="https://ghbtns.com/github-btn.html?user=arjunpatel7&repo=alakazam-vgc&type=star&count=true&size=large" frameborder="0"
    \ scrolling="0" width="160px" height="30px"></iframe>
"""


# Display the GitHub star button in your Streamlit app


with st.sidebar:
    # create a description of the speedcheck bot in really fancy text
    st.header("What is alakazam")
    st.write(
        "alakazam allows you to pass natural language queries about Pokemon battle calculations, and it'll do the calc for you!"
    )
    st.write(
        "alakazam is NOT like chatgpt, so please be sure to ask only about speedchecks including the above info"
    )
    st.header("How does Alakazam-VGC work?")
    st.write(
        "This project uses some finetuned llms to pasre input game state descriptions from players to parseable Json strings?\
             which are passed to internal game logic to calculate outcomes"
    )
    st.write(
        "Many players use online damage calculators, which can take up to 1 minute to calculate a single game state"
    )
    st.write(
        "Whereas alakazam can calculate a query from input to result in under 10s when hot"
    )
    st.write(
        "Using LLMs can also allow us to (eventually) batch process inputs, and maybe even suggest optimal teambuilding strategies"
    )
    st.header("Check us out on Github!")
    st.link_button("Github", github_url)
    st.markdown(github_star_button, unsafe_allow_html=True)


# I want to include three columns here instead of query examples, that are drop down
# for Speed Checks, Optimal Evs, and BST queries

st.subheader("Ask alakazam about Pokemon battle calculations!")
q1, q2, q3 = st.columns(3)

with q1:
    st.subheader("Speed Checks")
    with st.expander(
        "Ask alakazam about common speed checks using stat changes, evs, and the pokemon of interest"
    ):
        st.write("Is -5 35 Noibat slower than -5 19 Blissey")
        st.write("Will Finneon with 230 speed evs outspeed Meowth with 215 speed evs")
        st.write("Does max speed Salamence outspeed 248 Talonflame?")

with q2:
    st.subheader("EV Optimal Training for knockouts")
    with st.expander("Ask alakazam to calculate optimal evs for a given game state"):
        st.write("/train Charizard to ohko Eevee using overheat")
        st.write("Train Hippowdon with banded using fire-punch to 2hko Dipplin")
        st.write(
            "Train Gimmighoul using karate-chop to 1hko Volcarona with 13 special-attack  1 special-defense and 29 defense and 9 hp."
        )
with q3:
    st.subheader("Base Stat Queries")
    with st.expander("Ask about base stats or base stat totals!"):
        st.write("What is the base special defense of Meowth?")
        st.write("What is Pikachu's speed stat?")


st.subheader("Ask away!")
input_prompt = st.text_input(label="Write your query here")


# I want to give users the ability to add queries to a cache, then compute all queries at once
# Below is the streamlit code for this

# if st.button("Add to cache"):
#     st.session_state.cache.append(input_prompt)
#     st.write(st.session_state.cache)


if input_prompt != "":
    # classify the intent of the input prompt
    # I would like to refactor this later so we avoid the intent classification
    # or, retrain the intent classifier to accept the train usecase
    train_shortcut = ["train", "calculate", "\train", "/train"]

    train_condition = [i for i in train_shortcut if i in input_prompt]

    # if the intent is speedcheck, run the speedcheck code
    if any(train_condition):
        st.write("Optimal ev calculating...")
        get_train_calc(input_prompt)
    else:
        response = classify_intent(input_prompt)
        st.write(response)
        if response == "speed check":
            get_speedcheck(input_prompt)
        elif response == "sql query":
            st.write("bst check")
            result = handle_query(input_prompt)
            st.write(result)
        else:
            st.write(
                "Sorry, I didn't understand that. Could you rephrase your to be a speedcheck or bst?"
            )


def send_speed_calc_error_report(incorrect_explanation):
    # grab most recent entry in history
    wrong_result = st.session_state.session_history[-1]

    report = {
        "query": wrong_result["query"],
        "wrong_explanation": incorrect_explanation,
        "p1": wrong_result["p1"],
        "p2": wrong_result["p2"],
        "p1_final_speed": wrong_result["p1_final_speed"],
        "p2_final_speed": wrong_result["p2_final_speed"],
        "p1_stat_changes": wrong_result["p1_stat_changes"],
        "p2_stat_changes": wrong_result["p2_stat_changes"],
        "p1_ev": wrong_result["p1_ev"],
        "p2_ev": wrong_result["p2_ev"],
        "convo_id": st.session_state.convo_id,
    }
    # write the report, along with the status of the application to the supabase table
    supabase_client = create_client(sb_url, sb_key)
    supabase_client.table("speed-checks-error-reports").insert(report).execute()


form_expander = st.expander("Report incorrect response")
with form_expander:
    if input_prompt != "":
        with st.form("Report Form") as form:
            # response was wrong for some reason
            st.write(
                "hey, sorry about that! Can you fill this out to help us tune the model better?"
            )
            # create a response box for the user to explain what happened
            incorrect_explanation = st.text_input(label="What went wrong?")
            send_report = st.form_submit_button("Send report!")
            if send_report:
                send_speed_calc_error_report(incorrect_explanation)
                st.write("Report sent! Thank you for your feedback!")
                # reset the form submission variable


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
