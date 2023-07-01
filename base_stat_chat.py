import argparse
from calculations import read_in_pokemon, extract_stat
from langchain import Cohere, SQLDatabase, SQLDatabaseChain
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# a chatbot for doing natural language querying on a dataset of pokemon stats

# we will use Langchain, Cohere, chains to accomplish this

# this will be a command line script that accepts the query and returns the result

pokemons = read_in_pokemon("gen9_pokemon.jsonl")

# convert pokemons to just pokemon and associated stats in columns

pokemon_stats = []


print(pokemons[0]["stats"])
for p in pokemons:
    pokemon_stats.append(
        {
            "name": str(p["name"]),
            "hp": int(extract_stat(p, "hp")),
            "attack": int(extract_stat(p, "attack")),
            "defense": int(extract_stat(p, "defense")),
            "specialattack": int(extract_stat(p, "special-attack")),
            "specialdefense": int(extract_stat(p, "special-defense")),
            "speed": int(extract_stat(p, "speed")),
        }
    )


# convert pokemon_stats to a sqlite database, and save it locally
# we will use this database to query the pokemon stats
# Your existing code

Base = declarative_base()


class Pokemon(Base):
    __tablename__ = "pokemon"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    hp = Column(Integer)
    attack = Column(Integer)
    defense = Column(Integer)
    specialattack = Column(Integer)
    specialdefense = Column(Integer)
    speed = Column(Integer)


def convert_to_sqlite(pokemon_stats, db_name="pokemon_stats.db"):
    engine = create_engine(f"sqlite:///{db_name}")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    for pokemon in pokemon_stats:
        p = Pokemon(
            name=str(pokemon["name"]),
            hp=int(pokemon["hp"]),
            attack=int((pokemon["attack"])),
            defense=int(pokemon["defense"]),
            specialattack=int(pokemon["specialattack"]),
            specialdefense=int(pokemon["specialdefense"]),
            speed=int(pokemon["speed"]),
        )
        session.add(p)

    session.commit()
    session.close()


def create_chain():
    llm = Cohere(model="command", temperature=0.90)
    db = SQLDatabase.from_uri("sqlite:///pokemon_stats.db")
    chain = SQLDatabaseChain.from_llm(llm, db, verbose=True)
    return chain


def run_query(chain, query):
    return chain.run(query)


parser = argparse.ArgumentParser(description="A chatbot for querying pokemon stats")
parser.add_argument("ask", type=str, help="The query to run")

args = parser.parse_args()
ask = args.ask

if __name__ == "__main__":
    chain = create_chain()
    print(run_query(chain, ask))

# we need to convert my json file of pokemon stats into a sqlite database
