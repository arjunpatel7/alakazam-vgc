import requests
from bs4 import BeautifulSoup


# In this script, we will scrape Serebii website for the series 4 newly legal pokemon

# We just need the names which we will pass to the pokeapi to get stats


url = "https://serebii.net/scarletviolet/rankedbattle/season8.shtml"  # Replace with the URL of the webpage containing the table
response = requests.get(url)
html_content = response.text

soup = BeautifulSoup(html_content, "html.parser")

td_elements = soup.find_all("td", align="center", class_="fooinfo")

# print(td_elements)


new_pokemon_series_4 = []

for td in td_elements:
    link = td.find("a")
    if link:
        # what parameters does this function take?

        text = link.get_text(separator=" ", strip=True)
        english_text = text.split(" ")[0]
        new_pokemon_series_4.append(english_text.lower())


# for specific pokemon, add them manually
# also, find index of charmander and remove everything above it


# manually add the pokemon that are not in the list

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

# merge both lists
new_pokemon_series_4 = new_pokemon_series_4 + additional_pokemon_forms

# drop duplicates
new_pokemon_series_4 = list(set(new_pokemon_series_4))

# now, we combine this information with the pokemon data we have from the pokeapi


# but, we have to refactor the data collection script to make it more modular
# then, we can simply use the functions we made there, here!
