# :dizzy: alakazam :spoon: : A command line interface for Pokemon VGC calculations

alakazam is a chatbot-like interface for running calculations for the Pokemon video games Pokemon Scarlet and Pokemon Violet, specifically for standard doubles (VGC) competitive play. Think of it like a standard damage calculator, except with natural language instructions instead!

Simply type in a calculation you wish to compute, and the app will parse your natural language instructions and return the result, just like magic!

alakazam works for three styles of intents: speed checks, optimal ev calculations (aka "/train"), and querying over base stat totals for Pokemon. It is currently deployed on Streamlit Cloud, and uses a finetuned large language model to parse user commands.


## Table of Contents
- [Usage](#usage)
- [How It Works](#how-it-works)
- [Stack](#stack)
- [Features](#features)
- [Roadmap](#roadmap)
- [License](#license)
- [Contact Information](#contact-information)

## Usage

Navigate to the deployed [Streamlit web application here](https://alakazam-vgc.streamlit.app).

From here, just type in a natural language command and hit enter! It may take up to fifteen seconds to get your first response. After submitting a few responses, latency should decrease to about four seconds.

Submitted results are cached in the app so you can keep track of your calcs.

## How it Works
When VGC players communicate the game state of a Pokemon match, they use a certain lingo usually called a damage calc. I wanted to know if I could train a large language model to parse these damage calcs and speed checks, to compute them directly instead of tediously using a interface like Pokemon Damage Calculator.


Alakazam uses an augmented finetuned large langauge model to compute speed checks. A pretrained large langauge model was instruction finetuned using LoRA techniques on a synthetic dataset containing pokemon names in a formatted calc phrasing. After parsing the damage calc, the model passes this information to a set of scripts to do the actual math. The results are returned directly back to the user, much like a computer command line interface.

## Intents

Alakazam can parse three types of intents: speed checks, optimal ev calculations, and querying over base stat totals for Pokemon.

### A note on intents.

All intents are still in development, and there will be bugs! If you notice an issue, please open an issue and describe the query that failed. I'll get to work as soon as I can!


### Speed Checks
A speed check consists of two pokemon, their stat stages, their investment in the speed stat, and that's it!

Instead of typing in 252 speed, you can also say "max speed".

An example of a speed check would be the following:
- Does max speed Salamence outspeed 248 Talonflame?

### Optimal EV Calculations (aka /train feature)

Often, players want to know how to optimally invest their EVs to one-hit ko, or two-hit ko, a certain Pokemon. This is a more complex calculation, and requires more information than a speed check.

alakazam can take natural language descriptions of the game state in addition to the pokemon names and moves, in order to quickly facilitate optimal ev calculation.

In order to do this, simply construct a query beginning with "/train" and then describe the condition in which you want a Pokemon to ohko another. Please include the following info, at minimum:
- The attacking Pokemon
- The defending Pokemon
- The move used (the name of the move will suffice)

You may also include the following info, if you know it:
- The attacking Pokemon's item (choice band, life orb, a 1.2x item referred as boosted, and choice specs)
- The defending Pokemon's item
- the weather
- the defending Pokemon's nature, stat distribution
- the tera types of the attacking and/or defending pokemon

An example of this query would be the following:
- /train Charizard to ohko Eevee using overheat
- /train banded Hippowdon using fire-punch to 2hko Dipplin

### Querying over base stat totals for Pokemon

You can also ask natural language questions about the base stats of Pokemon, and alakazam will run a SQL query to find the answer for you.

For example, you may ask:
- What is the base stat total of Charizard?
- what is the speed stat of Pikachu?



## Stack

We use [Streamlit](https://streamlit.io) for the web application, and Streamlit Cloud to host it.

We use [Modal](https://modal.com) to host a finetuned large language model model for parsing user commands.

We use [langchain](https://api.python.langchain.com/en/latest/) to generate examples, and we use [PokeAPI](https://pokeapi.co) to get the data about the games and Pokemon for the app to lookup.

We use [Supabase](https://supabase.com) to store queries made by users, so we can learn about what users request and what calcs work.

We use [Hugging Face](https://huggingface.co) (transformers, peft) and [Google Colab](https://colab.research.google.com) to finetune an instance of a 560million parameter [BLOOM](https://huggingface.co/bigscience/bloom-560m#uses) model from BigScience.


## Features

- Fast calculation of natural language speed checks for Pokemon VGC
- ohko and 2hko optimality calcs given natural language desciptions of the game state
- Natural language querying of pokemon stats
- History to keep track of previous calculations
- Report incorrect statistics to the maintainer

## Safety

When using large language models such as BLOOM, we must be careful to warn users about potentially inappropriate and errand output that these models can generate.

The current implementation of alakazam does not allow for free-form generation to be surfaced directly to users. Additionally, we check for output that we'd expect for our speed check calculations, and fail safely if we don't get a generation along those lines. In other words, it should not be possible to easily generate harmful content with this app.

If you see inappropriate or offensive output generated by this model, please contact the repo maintainer Arjun Patel with a screenshot and prompt used to obtain this behavior. Thanks!

## Acknowledgements

Shoutout to Chris Alexiuk for his finetuning script with LoRa/PEFT, which is what I modified to train my model.

Thanks to Full Stack Deep Learning's free online LLM Bootcamp, where I learned how to use Modal and how to think about structuring my web application.

## License

The underlying bloom model uses the BigScience Bloom RAIL 1.0 License. Please be aware that any derivatives of this application will have to incorporate this license.

References to Pokemon are property, trademark, copyright of Nintendo and the Pokemon Company International, not myself.

