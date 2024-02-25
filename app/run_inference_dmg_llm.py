from modal import Image, Stub, method, Secret, gpu
import time


model_name = "llama-vgc-dmg-parser-v1"

# download model function
def download_model():
    from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
    from peft import PeftModel
    import os
    import torch

    model_name = "llama-vgc-dmg-parser-v1"

    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_double_quant=True,
        bnb_4bit_compute_dtype=torch.bfloat16,
    )

    peft_model_id = f"arjunpatel/{model_name}"

    # config = LoraConfig.from_pretrained(peft_model_id)

    model = AutoModelForCausalLM.from_pretrained(
        "meta-llama/Llama-2-7b-hf",
        quantization_config=bnb_config,
        device_map="auto",
        token=os.environ["HF_TOKEN"],
    )

    AutoTokenizer.from_pretrained(
        "meta-llama/Llama-2-7b-hf", token=os.environ["HF_TOKEN"]
    )

    PeftModel.from_pretrained(model, peft_model_id)


# creates docker image equivalent for Modal app


image = (
    Image.debian_slim(python_version="3.10.12")
    .pip_install(
        "transformers==4.37.2",
        "torch==2.1.0",
        "peft==0.8.2",
        #    "gradio==3.8",
        "editdistance==0.6.2",
        "jsonlines==3.1.0",
        "bitsandbytes==0.42.0",
    )
    .run_function(
        download_model,
        secrets=[Secret.from_name("my-huggingface-secret-2")],
        gpu=gpu.T4(count=1),
    )
)

# create separate stub for now. Later we will merge them
stub = Stub("pkmn-dmg", image=image)


# instantiate class for dmg calculator
@stub.cls(secrets=[Secret.from_name("my-huggingface-secret-2")], gpu=gpu.T4(count=1))
class PokemonDamageParser:
    def __enter__(self):
        # the enter function is for one-time initialization

        from transformers import (
            AutoTokenizer,
            AutoModelForCausalLM,
            BitsAndBytesConfig,
        )
        from peft import PeftModel
        import os
        import torch

        model_name = "llama-vgc-dmg-parser-v1"

        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_double_quant=True,
            bnb_4bit_compute_dtype=torch.bfloat16,
        )

        peft_model_id = f"arjunpatel/{model_name}"

        dmg_model = AutoModelForCausalLM.from_pretrained(
            "meta-llama/Llama-2-7b-hf",
            quantization_config=bnb_config,
            device_map="auto",
            token=os.environ["HF_TOKEN"],
            return_dict=True,
        )

        self.tokenizer = AutoTokenizer.from_pretrained(
            "meta-llama/Llama-2-7b-hf", token=os.environ["HF_TOKEN"]
        )
        self.tokenizer.pad_token = self.tokenizer.eos_token

        dmg_model = PeftModel.from_pretrained(dmg_model, peft_model_id)

        dmg_model.eval()
        # what does the line above do?
        # https://pytorch.org/docs/stable/generated/torch.nn.Module.html#torch.nn.Module.eval

        self.model = dmg_model

        # getting error about two devices, cuda:0 and cpu. Need to specify on cuda.

        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

    # next, we make the method that will generate text
    # we use the @method decorator to tell Modal
    # that this method should be run in the container
    # https://modal.com/docs/guide/lifecycle-functions

    @method()
    def generate(self, input, max_new_tokens=500, **kwargs):
        import torch

        batch = self.tokenizer(
            f"""
Please convert the input Pokemon battle description into JSON.\n\nInput:\n{input}\n
Response:\n
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
    def generate_batch(self, inputs, max_new_tokens=500, **kwargs):
        import torch

        # need to pad just in case stuff isn't same size
        def wrap_prompt(input):
            new_text = f"""
Please convert the input Pokemon battle description into JSON.\n\nInput:\n{input}\n
Response:\n
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


# write local entryways so we can test the model locally


@stub.function(image=image)
def run_inference(input):
    def predict(input):
        result = PokemonDamageParser().generate.remote(input, max_new_tokens=500)
        INSTRUCTION = f"""
Please convert the input Pokemon battle description into JSON.\n\nInput:\n{input}\n
Response:\n
"""
        result = result.replace(INSTRUCTION, "")

        return result

    return predict(input)


@stub.function(image=image)
def run_batch_inference(inputs):
    def predict(inputs):
        result = PokemonDamageParser().generate_batch.remote(inputs, max_new_tokens=200)
        for index, r in enumerate(result):
            INSTRUCTION = f"""
Please convert the input Pokemon battle description into JSON.\n\nInput:\n{input}\n
Response:\n
"""
            r = r.replace(INSTRUCTION, "")
            result[index] = r
        return result

    return predict(inputs)


@stub.local_entrypoint()
def main():
    start_time = time.time()
    inputs = [
        "Calculate Golduck using mega-punch to 2hko Hisui Sliggoo.",
        "/train Gimmighoul using karate-chop to 1hko Volcarona with 13 special-attack  1 special-defense and 29 defense and 9 hp."
        "Train Hippowdon with banded using fire-punch to 1hko Dipplin",
        "What are the optimal evs for Goodra to ohko Hakamo O using mega-punch?",
    ]
    model = PokemonDamageParser()
    response = model.generate.remote(inputs[0], max_new_tokens=500)
    print(response)
    print("Total time taken...")
    end_time = time.time()
    print(end_time - start_time)

    print("Trying multiple inputs...")

    start_time = time.time()

    response = model.generate_batch.remote(inputs, max_new_tokens=500)
    end_time = time.time()
    for r in response:
        print(r)
        print("/n")
    print("Total time...")
    print(end_time - start_time)
    print("Time per input...")
    print((end_time - start_time) / len(inputs))
