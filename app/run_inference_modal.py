from modal import Image, Stub, method, Secret, gpu
import time

# load model into Modal
model_name = "bloom-speed-check-expanded"


def download_model():
    from transformers import AutoTokenizer, AutoModelForCausalLM
    from peft import PeftModel, PeftConfig

    peft_model_id = f"arjunpatel/{model_name}"
    config = PeftConfig.from_pretrained(peft_model_id)
    m = AutoModelForCausalLM.from_pretrained(
        config.base_model_name_or_path,
        return_dict=True,
        load_in_8bit=False,
        device_map="auto",
    )
    AutoTokenizer.from_pretrained(config.base_model_name_or_path)

    PeftModel.from_pretrained(m, peft_model_id)


# creates docker image equivalent for Modal app
image = (
    Image.debian_slim(python_version="3.10")
    .pip_install(
        "transformers==4.23.1",
        "torch==2.0.1",
        "peft==0.3.0",
        #    "gradio==3.8",
        "editdistance==0.6.2",
        "jsonlines==3.1.0",
    )
    .run_function(download_model)
)

# Create and name Stub
stub = Stub("pkmn-py", image=image)

# In Modal, we can reuse the same container for multiple inputs
# So, we want to create a class that represents the modal and tokenizer
# using the @stub.cls decorator

# this will allow us to load the model once and reuse it.
# https://modal.com/docs/guide/lifecycle-functions

# use gpu.A100 for fastest inference, around 3s after startup
# t4 is cheaper and just as fast as a100
# use cpu to specify core, around 10s after startup


@stub.cls(secret=Secret.from_name("my-huggingface-secret"), gpu=gpu.T4(count=1))
class PokemonSpeedChecker:
    def __enter__(self):
        # the enter function is for one-time initialization

        import torch
        import os
        from transformers import AutoTokenizer, AutoModelForCausalLM
        from peft import PeftModel, PeftConfig

        model_name = "bloom-speed-check-expanded"

        peft_model_id = f"arjunpatel/{model_name}"
        config = PeftConfig.from_pretrained(peft_model_id)

        self.tokenizer = AutoTokenizer.from_pretrained(
            config.base_model_name_or_path,
            use_auth_token=os.environ["HUGGINGFACE_TOKEN"],
        )
        model = AutoModelForCausalLM.from_pretrained(
            config.base_model_name_or_path,
            return_dict=True,
            load_in_8bit=False,
            device_map="auto",
            use_auth_token=os.environ["HUGGINGFACE_TOKEN"],
        )
        speed_model = PeftModel.from_pretrained(model, peft_model_id)

        speed_model.eval()
        # what does the line above do?
        # https://pytorch.org/docs/stable/generated/torch.nn.Module.html#torch.nn.Module.eval

        self.model = speed_model

        # getting error about two devices, cuda:0 and cpu. Need to specify on cuda.

        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

    # next, we make the method that will generate text
    # we use the @method decorator to tell Modal
    # that this method should be run in the container
    # https://modal.com/docs/guide/lifecycle-functions

    @method()
    def generate(self, input, max_new_tokens=200, **kwargs):
        import torch

        batch = self.tokenizer(
            f"""
Given the following input, please parse it and return a valid JSON string with the corresponding arguments.\n\nInput:\n{input}\n
Output:\n
""",
            return_tensors="pt",
        )
        # was getting an error about not being on the same device, and this worked
        # so.... gonna just leave this here until I understand why this line specifically worked

        batch = batch.to(self.device)

        with torch.cuda.amp.autocast():
            output_tokens = self.model.generate(**batch, max_new_tokens=max_new_tokens)
        return self.tokenizer.decode(output_tokens[0], skip_special_tokens=True)

    @method()
    def generate_batch(self, inputs, max_new_tokens=200, **kwargs):
        import torch

        # need to pad just in case stuff isn't same size
        def wrap_prompt(input):
            new_text = f"""
Given the following input, please parse it and return a valid JSON string with the corresponding arguments.\n\nInput:\n{input}\n
Output:\n
"""
            return new_text

        inputs = [wrap_prompt(input) for input in inputs]
        batches = self.tokenizer(inputs, return_tensors="pt", padding=True).to(
            self.device
        )
        # presumably speeds up inference with mixed precision training
        with torch.cuda.amp.autocast():

            # generate output tokens for all batches
            output_tokens_list = self.model.generate(
                **batches, max_new_tokens=max_new_tokens
            )

        # list comprehension

        # outputs = self.tokenizer.decode(output_tokens_list[0], skip_special_tokens=True)

        outputs = [
            self.tokenizer.decode(output_tokens_list[i], skip_special_tokens=True)
            for i in range(len(inputs))
        ]

        return outputs


@stub.function(image=image)
def run_inference(input):
    def predict(input):
        result = PokemonSpeedChecker().generate.remote(input, max_new_tokens=200)
        INSTRUCTION = f"""
Given the following input, please parse it and return a valid JSON string with the corresponding arguments.\n\nInput:\n{input}\n
Output:\n
"""
        result = result.replace(INSTRUCTION, "")

        return result

    return predict(input)


@stub.function(image=image)
def run_batch_inference(inputs):
    def predict(inputs):
        result = PokemonSpeedChecker().generate_batch.remote(inputs, max_new_tokens=200)
        for index, r in enumerate(result):
            INSTRUCTION = f"""
Given the following input, please parse it and return a valid JSON string with the corresponding arguments.\n\nInput:\n{inputs[index]}\n
Output:\n
"""
            r = r.replace(INSTRUCTION, "")
            result[index] = r
        return result

    return predict(inputs)


@stub.local_entrypoint()
def main():
    start_time = time.time()
    inputs = [
        "Is -5 35 Noibat slower than -5 19 Blissey?",
        "Does -6 32 Larvesta outspeed -5 105 Arrokuda?",
        "Is -6 32 Larvesta slower than -5 105 Arrokuda?",
        "Will Finneon with 230 speed evs outspeed Meowth with 215 speed evs",
    ]
    model = PokemonSpeedChecker()
    response = model.generate.remote(inputs[0], max_new_tokens=200)
    print(response)
    print("Total time taken...")
    end_time = time.time()
    print(end_time - start_time)

    print("Trying multiple inputs...")

    start_time = time.time()

    response = model.generate_batch.remote(inputs, max_new_tokens=200)
    end_time = time.time()
    for r in response:
        print(r)
        print("/n")
    print("Total time...")
    print(end_time - start_time)
    print("Time per input...")
    print((end_time - start_time) / len(inputs))
