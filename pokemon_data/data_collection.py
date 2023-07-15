# refactored version of data_collection.ipynb
import jsonlines
from tqdm import tqdm
import requests
from bs4 import BeautifulSoup

# consts
paldea_pokedex = requests.get("https://pokeapi.co/api/v2/pokedex/paldea/")
paldea_pokemon = paldea_pokedex.json()["pokemon_entries"]
pokemon_game_info = "https://pokeapi.co/api/v2/pokemon/"

additional_pokemon_forms = [
    "raichu-alola",
    "dugtrio-alola",
    "meowth-alola",
    "persian-alola",
    "meowth-galar",
    "growlithe-hisui",
    "arcanine-hisui",
    "slowpoke-galar",
    "slowbro-galar",
    "slowking-galar",
    "muk-alola",
    "voltorb-hisui",
    "electrode-hisui",
    "articuno-galar",
    "zapdos-galar",
    "moltres-galar",
    "typhlosion-hisui",
    "qwilfish-hisui",
    "sneasal-hisui",
    "samurott-hisui",
    "lilligant-hisui",
    "zorua-hisui",
    "zoroark-hisui",
    "tornadus-therian",
    "thundurus-therian",
    "landorus-therian",
    "tornadus-incarnate",
    "thundurus-incarnate",
    "landorus-incarnate",
    "enamorus-incarnate",
    "enamorus-therian",
    "sliggoo-hisui",
    "goodra-hisui",
    "avalugg-hisui",
    "decidueye-hisui",
    "urshifu-rapid-strike",
    "urshifu-single-strike",
    "basculegion-male",
    "basculegion-female",
    "gimmighoul",
]


# functions needed to create the jsonls, general utilities

# wrap this in a function


def pokemon_entry_to_dict(pokemon_properties):
    # helper function for working with pokapi data
    pokemon_moves = pokemon_properties["moves"]
    pokemon_types = pokemon_properties["types"]
    pokemon_abilities = pokemon_properties["abilities"]
    pokemon_stats = pokemon_properties["stats"]
    pokemon_name = pokemon_properties["name"]

    pkmn_dict = {
        "name": pokemon_name,
        "moves": pokemon_moves,
        "types": pokemon_types,
        "abilities": pokemon_abilities,
        "stats": pokemon_stats,
        # should include id here
        "id": pokemon_properties["id"],
    }
    return pkmn_dict


def get_paldea_pokemon():
    # retrieves paldea pokedex pokemon from pokeapi
    pokemons = []
    for pokemon in tqdm(paldea_pokemon, desc="retrieving paldea pokemon"):
        pokemon_url = pokemon["pokemon_species"]["url"]
        # should really use pokemon id here instead of pokemon name. allows for the actual pokemon to appear if they have forms

        # instead of looking on name, look on url
        pokemon_properties = requests.get(
            pokemon_url.replace("pokemon-species", "pokemon")
        )

        pokemon_properties = pokemon_properties.json()
        pokemons.append(pokemon_entry_to_dict(pokemon_properties))

    return pokemons


# retrieving natures

# retrieving the series 4 additional pokemon, which are not in the paldea dex


def scrape_serebii_series_four_mons():
    url = "https://serebii.net/scarletviolet/rankedbattle/season8.shtml"  # Replace with the URL of the webpage containing the table
    response = requests.get(url)
    html_content = response.text

    soup = BeautifulSoup(html_content, "html.parser")

    td_elements = soup.find_all("td", align="center", class_="fooinfo")

    new_pokemon_series_4 = []

    for td in td_elements:
        link = td.find("a")
        if link:
            # what parameters does this function take?

            text = link.get_text(separator=" ", strip=True)
            english_text = text.split(" ")[0]
            new_pokemon_series_4.append(english_text.lower())

    # given list find index of "Charmander"
    charmander_index = new_pokemon_series_4.index("charmander")

    new_pokemon_series_4 = new_pokemon_series_4[charmander_index:]

    # manually add the pokemon that are not in the list

    # merge both lists
    new_pokemon_series_4 = new_pokemon_series_4 + additional_pokemon_forms

    # drop duplicates
    new_pokemon_series_4 = list(set(new_pokemon_series_4))

    new_pokemon_series_4 = list(filter(lambda x: x != "", new_pokemon_series_4))

    return new_pokemon_series_4


def get_series_four_pokemon(pokemon_series_four):
    # using names of series four pokemon, get the pokemon data from pokeapi

    # since we are using just the names, we will have to transform name to id
    # then retrieve the pokemon data from pokeapi
    pokemons = []
    for pokemon in tqdm(pokemon_series_four, desc="retrieving series four pokemon"):
        pokemon_properties = requests.get(pokemon_game_info + pokemon)
        try:
            pokemon_properties = pokemon_properties.json()
            pokemons.append(pokemon_entry_to_dict(pokemon_properties))
        except requests.exceptions.JSONDecodeError:
            # this pokemon likely has a form, so it needs the actual form name to properly retrieve the data
            # we can just skip it, since the other forms are in the list explicitly
            continue
    return pokemons


# combining everything together and writing it out
def write_all_pokemon(pokemons):
    # thanks chatgpt
    # if jsonl exists, delete it

    for p in pokemons:
        if p["name"] in additional_pokemon_forms:
            # split the name on dash and reverse it, then rejoin
            p["name"] = "-".join(p["name"].split("-")[::-1])

    with jsonlines.open("./data/gen9_pokemon.jsonl", mode="w") as w:

        w.write_all(pokemons)
    return


# this is the main function that will be called to create the jsonl file
if __name__ == "__main__":
    paldea_pokemon = get_paldea_pokemon()
    series_four_pokemon = scrape_serebii_series_four_mons()
    series_four_pokemon = get_series_four_pokemon(series_four_pokemon)
    # drop duplicates and combine
    # combine the paldea and series four pokemon

    all_pokemon = paldea_pokemon + series_four_pokemon
    write_all_pokemon(all_pokemon)
