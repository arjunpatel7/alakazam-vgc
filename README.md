# alakazam: A command line interface for Pokemon VGC calculations

alakazam is a chatbot-like interface for running calculations for the Pokemon video games Pokemon Scarlet and Pokemon Violet, specifically for standard doubles (VGC) competitive play. Think of it like a standard damage calculator, except with natural language instructions instead!

Simply type in a calculation you wish to compute, and the app will parse your natural language instructions and return the result.

Alakazam only works for speed checks right now, but advanced capabilites such as damage calcs are incoming! If there's something specific you'd want to see, please open an issue. Thanks, and enjoy!



## Table of Contents
- [Usage](#usage)
- [How It Works](#how-it-works)
- [Stack](#stack)
- [Features](#features)
- [Roadmap](#roadmap)
- [License](#license)
- [Contact Information](#contact-information)

## Usage

Navigate to the deployed [Streamlit web application here](https://alakazam.streamlit.app/).

From here, just type in a natural language command and hit enter! It may take up to fifteen seconds to get your first response. After submitting a few responses, latency should decrease to about four seconds.

Submitted results are cached in the app so you can keep track of your calcs.

## How it Works
When VGC players communicate the game state of a Pokemon match, they use a certain lingo usually called a damage calc. I wanted to know if I could train a large language model to parse these damage calcs and speed checks, to compute them directly instead of tediously using a interface like Pokemon Damage Calculator.


Alakazam uses an augmented finetuned large langauge model to compute speed checks. A pretrained large langauge model was instruction finetuned using LoRA techniques on a synthetic dataset containing pokemon names in a formatted calc phrasing. After parsing the damage calc, the model passes this information to a set of scripts to do the actual math. The results are returned directly back to the user, much like a computer command line interface.

## Stack

We use Streamlit for the web application, and Streamlit Cloud to host it.

We use Modal to host a finetuned large language model model for parsing user commands.

We use langchain to generate examples, and we use PokeAPI to get the data about the games and Pokemon for the app to lookup.

We use Supabase to store queries made by users, so we can learn about what users request and what calcs work.

We use Hugging Face (transformers, peft) and Google Colab to finetune an instance of a 560million parameter BLOOM model from BigScience.


## Features

- Fast calculation of natural language speed checks
- History to keep track of previous calculations

## Roadmap
- Add chatbot functionality (Retrieval Augmented Generation) to external useful data sources (like an items dictionary, or berry dict, or game knowledge)
- Add full damage calc capability

## License


