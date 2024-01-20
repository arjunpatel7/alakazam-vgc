import jsonlines


def read_in_pokemon(f):
    pokemons = []
    with jsonlines.open(f) as reader:
        for entry in reader:
            pokemons.append(entry)
    return pokemons


def pokemon_data():
    pokemons = read_in_pokemon("./data/gen9_pokemon.jsonl")
    return pokemons


pokemons = pokemon_data()


print(pokemons[3])
