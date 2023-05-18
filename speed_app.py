import streamlit as st
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from peft import PeftModel, PeftConfig
from calculations import formatted_speed_check
import re 
import ast


model_name = "bloom-speed-check-small"

peft_model_id = f"arjunpatel/{model_name}"
config = PeftConfig.from_pretrained(peft_model_id)
model = AutoModelForCausalLM.from_pretrained(config.base_model_name_or_path, return_dict=True, load_in_8bit=False, device_map='auto')
tokenizer = AutoTokenizer.from_pretrained(config.base_model_name_or_path)

# Load the Lora model
speed_model = PeftModel.from_pretrained(model, peft_model_id)



def make_inference(input):
  batch = tokenizer(f'''
Given the following input, please parse it and return a valid JSON string with the corresponding arguments. If the input contains the phrase "max speed", please assume that corresponds to 252 speed ev investment and stage change of 0 unless otherwise state.\n\nInput:\n{input}\n
Output:\n
''', return_tensors='pt')

  with torch.cuda.amp.autocast():
    output_tokens = speed_model.generate(**batch, max_new_tokens=200)

  return tokenizer.decode(output_tokens[0], skip_special_tokens=True)


def search_json_dict(string):
    # thx chatgpt
    pattern = r'{.*?}'
    match = re.search(pattern, string)
    if match:
        json_dict_string = match.group()
        return json_dict_string
    else:
        return None


# take prompt and grab the strings after output
import json
def get_speedcheck(prompt):
    instruction = f'''
Given the following input, please parse it and return a valid JSON string with the corresponding arguments. If the input contains the phrase "max speed", please assume that corresponds to 252 speed ev investment and stage change of 0 unless otherwise state.\n\nInput:\n{prompt}\n
Output:\n
'''
    try:
        result = make_inference(prompt).replace(instruction, "")
        # st.write(result)
    
        speedcheck_outcome = formatted_speed_check(result)
        #st.write(speedcheck_outcome)
        st.write(speedcheck_outcome)
    except:
        st.write("Sorry, I didn't understand that. Could you make sure to specify the pokemons, ev, and stat changes?")


st.title("Welcome to speedcheck bot!")
input_prompt = st.text_input(label = "Write your query here")

if input_prompt != "":
      get_speedcheck(input_prompt)

# input_prompt = "Tell me if max speed iron bundle outspeeds max speed iron hands"

# instruction = f'''
# Given the following input, please parse it and return a valid JSON string with the corresponding arguments. If the input contains the phrase "max speed", please assume that corresponds to 252 speed ev investment and stage change of 0 unless otherwise state.\n\nInput:\n{input_prompt}\n
# Output:\n
# '''

# output = get_speedcheck(input_prompt)


#print(ast.literal_eval(output))
#import json
#print(json.dumps(output))

# need to increase speed
# need to find why the model is returning entire instruction instead of just the generated part
# need to allow for multiple submissions at the same time
