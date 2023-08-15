import pandas as pd
import sqlite3
from sklearn.preprocessing import OneHotEncoder
from sklearn.preprocessing import LabelEncoder
import ast
from sklearn.feature_extraction.text import CountVectorizer
import re
import itertools
import json


label_encoder = LabelEncoder()
# Load data from the SQLite database
db_file_path = "C:\\Users\\azexl\\PycharmProjects\\Dota2PredictionMachine\\hero_data.db"
conn = sqlite3.connect(db_file_path)
data = pd.read_sql_query("SELECT * FROM hero_data", conn)
conn.close()

# Handling Missing Data: Drop rows with missing values (you can choose another strategy if needed)
data = data.dropna()

# One-hot encode the 'win_rate_color' column
encoder = OneHotEncoder(handle_unknown='ignore', sparse_output=False)
win_rate_color_encoded = encoder.fit_transform(data[['win_rate_color']])
win_rate_color_binary = (win_rate_color_encoded[:, 1] == 1).astype(int)
data['win_rate_color'] = win_rate_color_binary

# Create a mapping of hero names to integer codes
hero_name_to_code = {hero: i + 1 for i, hero in enumerate(data['hero_name'].unique())}

# Create an empty list to hold the formatted data for each hero
formatted_data = []

#Role_mapping
role_name_mapping = {
    'Carry': 0,
    'Mid': 1,
    'Offlane': 2,
    'Support (4)': 3,
    'Support (5)': 4
}

#hero dict
hero_list = [
    "Anti-mage", "Axe", "Bane", "Bloodseeker", "Crystal maiden", "Drow ranger", "Earthshaker", "Juggernaut",
    "Mirana",
    "Morphling", "Shadow fiend", "Phantom lancer", "Puck", "Pudge", "Razor", "Sand king", "Storm spirit",
    "Sven",
    "Tiny", "Vengeful spirit", "Windranger", "Zeus", "Kunkka", "Lina", "Lion", "Shadow shaman", "Slardar",
    "Tidehunter",
    "Witch doctor", "Lich", "Riki", "Enigma", "Tinker", "Sniper", "Necrophos", "Warlock", "Beastmaster",
    "Queen of pain",
    "Venomancer", "Faceless void", "Wraith king", "Death prophet", "Phantom assassin", "Pugna",
    "Templar assassin",
    "Viper", "Luna", "Dragon knight", "Dazzle", "Clockwerk", "Leshrac", "Nature's prophet", "Lifestealer",
    "Dark seer",
    "Clinkz", "Omniknight", "Enchantress", "Huskar", "Night stalker", "Broodmother", "Bounty hunter", "Weaver",
    "Jakiro",
    "Batrider", "Chen", "Spectre", "Ancient apparition", "Doom", "Ursa", "Spirit breaker", "Gyrocopter",
    "Alchemist",
    "Invoker", "Silencer", "Outworld destroyer", "Lycan", "Brewmaster", "Shadow demon", "Lone druid",
    "Chaos knight",
    "Meepo", "Treant protector", "Ogre magi", "Undying", "Rubick", "Disruptor", "Nyx assassin", "Naga siren",
    "Keeper of the light", "Io", "Visage", "Slark", "Medusa", "Troll warlord", "Centaur warrunner", "Magnus",
    "Timbersaw", "Bristleback", "Tusk", "Skywrath mage", "Abaddon", "Elder titan", "Legion commander", "Techies",
    "Ember spirit",
    "Earth spirit", "Underlord", "Terrorblade", "Phoenix", "Oracle", "Winter wyvern", "Arc warden",
    "Monkey king",
    "Dark willow", "Pangolier", "Grimstroke", "Hoodwink", "Void spirit", "Snapfire", "Mars", "Dawnbreaker", "Marci", "Primal beast", "Muerta"
]

# Create hero_dictionary using hero_list with sequential numbering
hero_dictionary = {"Anti-mage":1, "Axe":2, "Bane":3, "Bloodseeker":4, "Crystal maiden":5, "Drow ranger":6, "Earthshaker":7, "Juggernaut":8,
    "Mirana":9,
    "Morphling":10 , "Shadow fiend":11, "Phantom lancer":12, "Puck":13, "Pudge":14, "Razor":15, "Sand king":16, "Storm spirit":17,
    "Sven":18,
    "Tiny":19, "Vengeful spirit":20, "Windranger":21, "Zeus":22, "Kunkka":23, "Lina":25, "Lion":26, "Shadow shaman":27, "Slardar":28,
    "Tidehunter":29,
    "Witch doctor":30, "Lich":31, "Riki":32, "Enigma":33, "Tinker":34, "Sniper":35, "Necrophos":36, "Warlock":37, "Beastmaster":38,
    "Queen of pain":39,
    "Venomancer":40, "Faceless void":41, "Wraith king":42, "Death prophet":43, "Phantom assassin":44, "Pugna":45,
    "Templar assassin":46,
    "Viper":47, "Luna":48, "Dragon knight":49, "Dazzle":50, "Clockwerk":51, "Leshrac":52, "Nature's prophet":53 , "Lifestealer":54,
    "Dark seer":55,
    "Clinkz":56, "Omniknight":57, "Enchantress":58, "Huskar":59, "Night stalker":60, "Broodmother":61, "Bounty hunter":62, "Weaver":63,
    "Jakiro":64,
    "Batrider":65, "Chen":66, "Spectre":67, "Ancient apparition":68, "Doom":69, "Ursa":70, "Spirit breaker":71, "Gyrocopter":72,
    "Alchemist":73,
    "Invoker":74, "Silencer":75, "Outworld destroyer":76, "Lycan":77, "Brewmaster":78, "Shadow demon":79, "Lone druid":80,
    "Chaos knight":81,
    "Meepo":82, "Treant protector":83, "Ogre magi":84, "Undying":85, "Rubick":86, "Disruptor":87, "Nyx assassin":88, "Naga siren":89,
    "Keeper of the light":90, "Io":91, "Visage":92, "Slark":93, "Medusa":94, "Troll warlord":95, "Centaur warrunner":96, "Magnus":97,
    "Timbersaw":98, "Bristleback":99, "Tusk":100, "Skywrath mage":101, "Abaddon":102, "Elder titan":103, "Legion commander":104, "Techies":105,
    "Ember spirit":106,
    "Earth spirit":107, "Underlord":108, "Terrorblade":109, "Phoenix":110, "Oracle":111, "Winter wyvern":112, "Arc warden":113,
    "Monkey king":114,
    "Dark willow":119, "Pangolier":120, "Grimstroke":121, "Hoodwink":123, "Void spirit":126, "Snapfire":128, "Mars":129, "Dawnbreaker":135, "Marci":136, "Primal beast":137, "Muerta":138}



# Remove the '%' symbol from the 'win_rate' column and convert it to a numeric data type
# Check if the 'win_rate' column is already a string and convert if needed
if data['win_rate'].dtype == object:  # Check if the column is of type 'object' (string)
    data['win_rate'] = data['win_rate'].str.replace('%', '').astype(float)
else:  # If the column contains numeric values, use apply() to apply the replacement
    data['win_rate'] = data['win_rate'].apply(lambda x: float(str(x).replace('%', '')))

#hero_mapping
# Loop through hero_list PLACE ALL RE-FORMAT LOGIC HERE.
for hero_name, matches, win_rate, win_rate_color, viable_roles, role_stats, synergy_info in zip(
        data['hero_name'], data['matches'], data['win_rate'], data['win_rate_color'], data['viable_roles'],
        data['role_stats'], data['synergy']
):

    # Convert 'viable_roles' to numericals using role_name_mapping
    numerical_roles = []
    for role in ast.literal_eval(viable_roles):
        if role in role_name_mapping:
            numerical_roles.append(role_name_mapping[role])
        else:
            # Handle unknown roles if necessary (e.g., you might want to skip them or assign a special value)
            numerical_roles.append(-1)  # For example, use -1 to represent an unknown role

#loop that checks for role in role_name_mapping. if role is found, it saves the name of the role and runs through RE's below.
    #every time theres a \n in role_stats it creates a column made of whatever comes before it.
    role_name = []
    role_matches = []
    role_win_rate = []
    role_win_rate_color = []
    role_columns = []
    captured_text_list = []
    hero_segments = role_stats.split("\n")
    for r in hero_segments:
        role_strip = r.strip()
        captured_text_list.append(role_strip)
        role_head = re.findall(r'Carry|Mid|Offlane|Support \(4\)|Support \(5\)', role_strip)
        for rul in role_head:
            role_name.append(role_name_mapping[rul])
            role_matches_result = re.search(r'Mid (\d+)|Offlane (\d+)|Support \(4\) (\d+)|Carry (\d+)|Support \(5\) (\d+)',
                                            role_strip)
            if role_matches_result:
                # The regular expression found a match
                role_matches.extend([int(val) for val in role_matches_result.groups() if val is not None])
            else:
                continue
            role_win_rate_result = re.search(r'(\d+\.\d+)%\s+(green|red)', role_strip)
            if role_win_rate_result:
                # The regular expression found a match
                role_win_rate.append(float(role_win_rate_result.group(1)))
                role_win_rate_color.append(role_win_rate_result.group(2))
                for i in range(len(role_win_rate_color)):
                    if role_win_rate_color[i] == 'green':
                        role_win_rate_color[i] = 1
                    elif role_win_rate_color[i] == 'red':
                        role_win_rate_color[i] = 0
                #convert color to numerical

            else:
                continue

    #SYNERGY LOGIC -
    # split WITH and AGAINST.
    with_info = []
    against_info = []
    pattern = r"(with|against) (.+):\n(\d+\.\d+%) (\w+) \((\d+-\d+)\)"
    synergy_matches = re.findall(pattern, synergy_info)

    for match in synergy_matches:
        # Regular expressions to match the required patterns
        if match[0] == "with":
            with_info.append(str(match))
        elif match[0] == "against":
            against_info.append(str(match))

    #convert (against, anti-mage, 53.0%, green (33-33)) to numbers.
    # to (1, 53, 0, 33, 33)
    numerical_with_info = []
    # Process each entry in the 'with_info' list
    for w in with_info:
        with_hero_number = None
        # Extract individual components from the entry
        components = w.strip("()").split(", ")
        with_hero = components[1].strip("'")

        if with_hero in hero_list:
            # Convert the hero name to numerical code
            with_hero_number = hero_dictionary[with_hero]

        with_win_rate = float(components[2].strip("'").rstrip('%'))
        with_color = 1 if components[3].strip("'") == "green" else 0
        with_matches = components[4].strip("'").split('-')
        with_matches_total = int(with_matches[1]) + int(with_matches[0])

        # Append the numerical values to the list
        numerical_with_info.append((with_hero_number, with_win_rate, with_color, with_matches, with_matches_total))

    #Process each entry in the 'against_info' list
    numerical_against_info = []
    for a in against_info:
        against_hero_number = None
        # Extract individual components from the entry
        components = a.strip("()").split(", ")
        against_hero = components[1].strip("'")

        if against_hero in hero_list:
            # Convert the hero name to numerical code
            against_hero_number = hero_dictionary[against_hero]

        against_win_rate = float(components[2].strip("'").rstrip('%'))
        against_color = 1 if components[3].strip("'") == "green" else 0
        against_matches = components[4].strip("'").split('-')
        against_matches_total = int(against_matches[1]) + int(against_matches[0])

        # Append the numerical values to the list
        numerical_against_info.append((against_hero_number, against_win_rate, against_color, against_matches, against_matches_total))

    # END OF LOOP THROUGH. Combine all information into a single string for each hero

    hero_code = hero_name_to_code[hero_name]
    hero_info_dict = {
        'hero_code': hero_code,
        'matches': matches,
        'win_rate': win_rate,
        'win_rate_color': win_rate_color,
        'numerical_roles': numerical_roles,
        'role_name': role_name,
        'role_matches': role_matches,
        'role_win_rate': role_win_rate,
        'role_win_rate_color': role_win_rate_color,
        'numerical_with_info': numerical_with_info,
        'numerical_against_info': numerical_against_info
    }


    # Append the formatted information to the list
    formatted_data.append(hero_info_dict)

# Create a DataFrame with the formatted data
formatted_df = pd.DataFrame(formatted_data)

# Assuming you have a DataFrame called "df" containing your data
formatted_df.to_csv('dota2protracker.csv', index=False)

# Print the formatted DataFrame
pd.set_option('display.max_colwidth', None)  # Set to display full contents of each cell
print(formatted_df)