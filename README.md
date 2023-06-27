# alakazam: A command line interface for Pokemon VGC calculations

alakazam is a chatbot-like interface for running calculations for the Pokemon video games Pokemon Scarlet and Pokemon Violet, specifically for standard doubles (VGC) competitive play. Think of it like a standard damage calculator, except with natural language instructions instead!

Simply type in a calculation you wish to compute, and the app will parse your natural language instructions and return the result.

Alakazam only works for speed checks right now, but advanced capabilites such as damage calcs are incoming! If there's something specific you'd want to see, please open an issue. Thanks, and enjoy!



## Table of Contents
- [Usage](#usage)
- [How it Works] (#how it works)
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

## Stack

We use Streamlit for the web application, and Streamlit Cloud to host it.

We use Modal to host a finetuned large language model model for parsing user commands.

We use langchain to generate examples


## Features

## Roadmap

## License

## Contact Information

