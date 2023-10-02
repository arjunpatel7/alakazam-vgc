# Main script for generating the intent classifier dataset
import pandas as pd


# read data from jsonl file in pandas

import jsonlines

# read in the speedcheck data, and convert to pandas dataframe
# with prompt and class columns


speedcheck_data = "./data/speed_training_data.jsonl"
query_data = "./data/query_prompts.jsonl"

with open(speedcheck_data, "r") as f:
    speedcheck_data = pd.DataFrame(jsonlines.Reader(f))

with open(query_data, "r") as f:
    query_data = pd.DataFrame(jsonlines.Reader(f))

query_data.columns = ["prompt"]
speedcheck_data = speedcheck_data[["prompt"]]
speedcheck_data = speedcheck_data.sample(n=500, random_state=1).reset_index(drop=True)

speedcheck_data["class"] = "speed check"

query_data["class"] = "sql query"

# make the last 500 rows unrelated
query_data["class"][-500:] = "unrelated"

# combine the two dataframes

combined_data = pd.concat([speedcheck_data, query_data])

# remove new lines from the data
combined_data["prompt"] = combined_data["prompt"].str.replace("\n", " ")
# if a prompt has a question mark, and additional text after the question mark,
# take the text after the question mark and put it in the prompt column as a new prompt

combined_data = combined_data.sample(frac=1, random_state=1).reset_index(drop=True)


# write out to csv

combined_data.to_csv("./data/intent_classifier_dataset.csv", index=False)
