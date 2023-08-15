import requests
import json
import time
import pandas as pd
from bs4 import BeautifulSoup
import sqlite3


# List of hero names
hero_list = [
    "Anti-Mage", "Axe", "Bane", "Bloodseeker", "Crystal%20Maiden", "Drow%20Ranger", "Earthshaker", "Juggernaut",
    "Mirana",
    "Morphling", "Shadow%20Fiend", "Phantom%20Lancer", "Puck", "Pudge", "Razor", "Sand%20King", "Storm%20Spirit",
    "Sven",
    "Tiny", "Vengeful%20Spirit", "Windranger", "Zeus", "Kunkka", "Lina", "Lion", "Shadow%20Shaman", "Slardar",
    "Tidehunter",
    "Witch%20Doctor", "Lich", "Riki", "Enigma", "Tinker", "Sniper", "Necrophos", "Warlock", "Beastmaster",
    "Queen%20of%20Pain",
    "Venomancer", "Faceless%20Void", "Wraith%20King", "Death%20Prophet", "Phantom%20Assassin", "Pugna",
    "Templar%20Assassin",
    "Viper", "Luna", "Dragon%20Knight", "Dazzle", "Clockwerk", "Leshrac", "Nature's%20Prophet", "Lifestealer",
    "Dark%20Seer",
    "Clinkz", "Omniknight", "Enchantress", "Huskar", "Night%20Stalker", "Broodmother", "Bounty%20Hunter", "Weaver",
    "Jakiro",
    "Batrider", "Chen", "Spectre", "Ancient%20Apparition", "Doom", "Ursa", "Spirit%20Breaker", "Gyrocopter",
    "Alchemist",
    "Invoker", "Silencer", "Outworld%20Destroyer", "Lycan", "Brewmaster", "Shadow%20Demon", "Lone%20Druid",
    "Chaos%20Knight",
    "Meepo", "Treant%20Protector", "Ogre%20Magi", "Undying", "Rubick", "Disruptor", "Nyx%20Assassin", "Naga%20Siren",
    "Keeper%20of%20the%20Light", "Io", "Visage", "Slark", "Medusa", "Troll%20Warlord", "Centaur%20Warrunner", "Magnus",
    "Timbersaw", "Bristleback", "Tusk", "Skywrath%20Mage", "Abaddon", "Elder%20Titan", "Legion%20Commander", "Techies",
    "Ember%20Spirit",
    "Earth%20Spirit", "Underlord", "Terrorblade", "Phoenix", "Oracle", "Winter%20Wyvern", "Arc%20Warden",
    "Monkey%20King",
    "Dark%20Willow", "Pangolier", "Grimstroke", "Hoodwink", "Void%20Spirit", "Snapfire", "Mars", "Dawnbreaker", "Marci", "Primal%20Beast", "Muerta"
]

# SQLite database connection
conn = sqlite3.connect("protracker_data.db")
c = conn.cursor()

# Create table for hero data
c.execute('''CREATE TABLE IF NOT EXISTS hero_data
             (hero_name TEXT PRIMARY KEY, matches INT, win_rate TEXT, win_rate_color TEXT, viable_roles TEXT, role_stats TEXT, synergy TEXT)''')

# Create a Pandas DataFrame to hold the hero data
hero_df = pd.DataFrame(columns=["hero_name", "matches", "win_rate", "win_rate_color", "viable_roles", "role_stats", "synergy"])

# Loop through hero list
for hero_name in hero_list:
    # Prepare URL
    hero_url = f"https://www.dota2protracker.com/hero/{hero_name}#"

    # Send HTTP request
    response = requests.get(hero_url)
    if response.status_code != 200:
        print(f"Failed to fetch data for {hero_name}")
        continue

    # Parse HTML
    soup = BeautifulSoup(response.content, 'html.parser')

    # Scrape header information
    hero_header = soup.find("div", class_="hero-header-stats-detailed")
    header = ""
    if hero_header:
        matches = hero_header.find("span", class_="yellow").text.strip()
        win_rate_element = hero_header.find("span", class_=["red", "green"])
        win_rate = win_rate_element.text.strip() if win_rate_element else ""
        win_rate_color = win_rate_element.get("class")[0] if win_rate_element else ""
        header = f"Matches: {matches} | Win Rate: {win_rate} ({win_rate_color}) "

    # Scrape Role information
    tabcount = [1, 2, 3, 4, 5]
    roles = []
    role_info = ""
    for tab in tabcount:
        role_tabs = soup.find(lambda tag: tag.name == "button" and tag.has_attr("id") and f"tabs-{tab}" in tag["id"])
        if role_tabs:
            role_name = role_tabs.find("svg").find_next_sibling(text=True).strip()
            roles.append(role_name)
            tab_info = soup.find(
                lambda tag: tag.name == "div" and tag.has_attr("class") and f"tabs-{tab}" in tag["class"])
            if tab_info:
                yellow_spans = tab_info.find_all("span", class_="yellow")
                if len(yellow_spans) >= 2:
                    second_yellow_span = yellow_spans[1]
                    role_matches = second_yellow_span.text.strip()
                role_percent = tab_info.find("span", class_=["red", "green"]).text.strip()
                role_color_element = tab_info.find("span", class_=["red", "green"])
                role_color = role_color_element.get("class")[0] if role_color_element else ""
                role_info += f"{role_name} {role_matches} {role_percent} {role_color}\n"
            else:
                print(f"No tab info found for tab {tab}")
        else:
            print(f"No role tabs found for tab {tab}")

    # Scrape Synergy Information
    synergy_data = []
    synergy_table = soup.find("tbody")
    if synergy_table:
        hero_names = [hero_name]
        for row in synergy_table.find_all("tr"):
            columns = row.find_all("td")
            if len(columns) == 3:
                hero = columns[0].find("a").get("href").split("/")[-1].capitalize()
                synergy_span = columns[1].find("span")
                synergy_matches = ""
                synergy = ""
                synergy_color = ""
                if synergy_span:
                    synergy = synergy_span.text.strip()
                    synergy_color = synergy_span.get("class")[0]
                    synergy_matches = synergy_span.next_sibling.strip() if synergy_span.next_sibling else ""

                counter_span = columns[2].find("span")
                counter_matches = ""
                counter = ""
                counter_color = ""
                if counter_span is not None:
                    counter = counter_span.text.strip()
                    counter_color = counter_span.get("class")[0] if counter_span.get("class") else ""
                    counter_matches = counter_span.next_sibling.strip() if counter_span.next_sibling else ""

                if hero != hero_name:
                    hero_names.append(hero)
                    synergy_data.append((f"with {hero}", synergy, synergy_color, synergy_matches))

                synergy_data.append((f"against {hero}", counter, counter_color, counter_matches))
            else:
                print(f"No synergy table found for {hero_name}")

    # Combine hero names and update synergy data
    synergy_data_combined = []
    for hero in hero_names:
        hero_synergy = [hero]
        for data in synergy_data:
            if data[0].startswith("with") and data[0].endswith(hero):
                hero_synergy.append(f"WITH {data[1]} {data[2]} {data[3]}.")
            elif data[0].startswith("against") and data[0].endswith(hero):
                hero_synergy.append(f"AGAINST {data[1]} {data[2]} {data[3]}.")
        synergy_data_combined.append(" ".join(hero_synergy))

    # Save data to SQLite database
    synergy_info = "\n".join([f"{data[0]}:\n{data[1]} {data[2]} {data[3]}" for data in synergy_data])
    c.execute(
        "INSERT INTO hero_data (hero_name, matches, win_rate, win_rate_color, viable_roles, role_stats, synergy) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (hero_name, matches, win_rate, win_rate_color, f"Viable roles: {roles}\n", f"\nRole Stats:\n{role_info}", synergy_info))

    # Save data to the DataFrame
    hero_df = pd.concat([hero_df, pd.DataFrame({"hero_name": [hero_name],
                                                "matches": [matches],
                                                "win_rate": [win_rate],
                                                "win_rate_color": [win_rate_color],  # Include the win_rate_color here
                                                "viable_roles": [f"{roles}\n"],
                                                "role_stats": [f"{role_info}\n"],
                                                "synergy": [synergy_info]})], ignore_index=True)
    # Delay between requests
    time.sleep(1)

# Save the DataFrame to the database
hero_df.to_sql("hero_data", conn, if_exists="replace", index=False)

# Commit changes and close the database connection
conn.commit()
conn.close()


# SQLite database connection
conn = sqlite3.connect("protracker_data.db")
c = conn.cursor()

# Execute SELECT query to retrieve all rows from the "hero_data" table
c.execute("SELECT * FROM hero_data")
rows = c.fetchall()

# Print the contents of the "hero_data" table
for row in rows:
    print(row)

# Close the database connection
conn.close()


