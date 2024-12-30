import requests
from bs4 import BeautifulSoup
import time
from dotenv import load_dotenv
import os

login_url = "https://archiveofourown.org/users/login"

session = requests.Session()

response = session.get(login_url)
if response.status_code == 200:

    soup = BeautifulSoup(response.content, "html.parser")

    token = soup.find("input", {"name": "authenticity_token"})["value"]
else:
    print("Failed to retrieve the login page.")
    exit()

load_dotenv()
username = os.getenv("USER_NAME")
password = os.getenv("PASSWORD")

payload = {
    "user[login]": username,
    "user[password]": password,
    "authenticity_token": token,
    "commit": "Log in",
}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Referer": login_url
}

login_response = session.post(login_url, data=payload, headers=headers)

fic_data = []

if login_response.status_code == 200:
    print("Login attempt completed.")

    if "My Dashboard" in login_response.text:
        print("Login successful!")

        for i in range(1, 3):
            time.sleep(5)
            new_page_response = session.get(f'https://archiveofourown.org/users/{username}/readings?page={i}')
            if new_page_response.status_code == 200:
                print("Successfully accessed the new page.")

                page = BeautifulSoup(new_page_response.content, "html.parser")

                raw_data = page.find("ol", class_="reading work index group")
                raw_indiv_items = raw_data.find_all("li", role="article")
                for item in raw_indiv_items:
                    if item.find("div", class_="header module") == None:
                        continue

                    header = item.find("div", class_="header module")
                    heading = header.find("h4")
                    title = heading.find_all("a")[0].text
                    raw_author = heading.find_all("a", rel="author")
                    author = []
                    if raw_author:
                        for entry in raw_author:
                            author.append(entry.text)
                    else:
                        author.append('Anonymous')

                    fandom_header = header.find("h5")
                    raw_fandoms = fandom_header.find_all("a", class_="tag")
                    fandoms = []
                    for fandom in raw_fandoms:
                        fandoms.append(fandom.text)

                    required_tags = header.find("ul", class_="required-tags")
                    raw_ratings = required_tags.find_all("li")[0]
                    raw_pairings = required_tags.find_all("li")[2]
                    ratings = raw_ratings.find("span", class_="text").text
                    pairings = raw_pairings.find("span", class_="text").text

                    raw_warnings = item.find("ul", class_="tags commas").find_all("li", class_="warnings")
                    raw_relationships = item.find("ul", class_="tags commas").find_all("li", class_="relationships")
                    raw_characters = item.find("ul", class_="tags commas").find_all("li", class_="characters")
                    raw_freeforms = item.find("ul", class_="tags commas").find_all("li", class_="freeforms")

                    warnings = []
                    relationships = []
                    characters = []
                    freeforms = []

                    for warning in raw_warnings:
                        warnings.append(warning.find("a", class_="tag").text)
                    for relationship in raw_relationships:
                        relationships.append(relationship.find("a", class_="tag").text)
                    for character in raw_characters:
                        characters.append(character.find("a", class_="tag").text)
                    for tag in raw_freeforms:
                        freeforms.append(tag.find("a", class_="tag").text)

                    raw_stats = item.find("dl", class_="stats")

                    lang = raw_stats.find("dd", class_="language").text
                    words = int(raw_stats.find("dd", class_="words").text.replace(",", ""))

                    raw_footer = item.find("h4", class_="viewed heading").text.split("\n")
                    listed_footer = list(filter(lambda x: x.strip(), raw_footer))
                    raw_date = listed_footer[0].split(" ")
                    raw_read_count = listed_footer[-1].split(" ")
                    date = int(raw_date[-1])
                    read_count = 0
                    if raw_read_count[-2].isnumeric():
                        read_count = int(raw_read_count[-2])
                    else:
                        read_count = 1

                    fic_data.append({
                        'title': title,
                        'author(s)': author,
                        'fandom(s)': fandoms,
                        'ratings': ratings,
                        'pairings': pairings,
                        'warnings': warnings,
                        'relationships': relationships,
                        'characters': characters,
                        'freeforms': freeforms,
                        'language': lang,
                        'word_count': words,
                        'last_read': date,
                        'read_count': read_count,
                    })
            else:
                print("Page traversal failed")
                exit()
    else:
        print("Login failed. Check your credentials or the token.")
else:
    print(f"Login request failed with status code {login_response.status_code}")

key_val = [2024]
filtered_data = list(filter(lambda x: x['last_read'] in key_val, fic_data))
fic_data = filtered_data

word_count = 0
for fic in fic_data:
    word_count = word_count + fic['word_count']
print(f"Total Word Count: {word_count}")
print()

print(f"Total fic count: {len(fic_data)}")
print()

tag_count = {}
for fic in fic_data:
    for tag in fic['freeforms']:
        if tag in tag_count.keys():
            tag_count[tag] += 1
        else:
            tag_count[tag] = 1

sorted_tags = dict(sorted(tag_count.items(), key=lambda x: x[1], reverse=True))
print("Top tags")
for tag in sorted_tags.keys():
    print(f"{tag}: {sorted_tags[tag]}")
print()

print("Top Relationships")
relationship_count = {}
for fic in fic_data:
    for rel in fic['relationships']:
        if rel in relationship_count.keys():
            relationship_count[rel] += 1
        else:
            relationship_count[rel] = 1

sorted_rels = dict(sorted(relationship_count.items(), key=lambda x: x[1], reverse=True))
for rels in sorted_rels.keys():
    print(f"{rels}: {sorted_rels[rels]}")
print()

print("Top Ratings")
ratings_count = {}
for fic in fic_data:
    if fic['ratings'] in ratings_count.keys():
        ratings_count[fic['ratings']] += 1
    else:
        ratings_count[fic['ratings']] = 1

sorted_rates = dict(sorted(ratings_count.items(), key=lambda x: x[1], reverse=True))
for rates in sorted_rates.keys():
    print(f"{rates}: {sorted_rates[rates]}")
print()

print("Favorite Characters")
character_count = {}
for fic in fic_data:
    for char in fic['characters']:
        if char in tag_count.keys():
            character_count[char] += 1
        else:
            character_count[char] = 1

sorted_chars = dict(sorted(character_count.items(), key=lambda x: x[1], reverse=True))
for char in sorted_chars.keys():
    print(f"{char}: {sorted_chars[char]}")
print()

print("Top Fandoms")
fandom_count = {}
for fic in fic_data:
    for fan in fic['fandom(s)']:
        if fan in fandom_count.keys():
            fandom_count[fan] += 1
        else:
            fandom_count[fan] = 1

sorted_fandom = dict(sorted(fandom_count.items(), key=lambda x: x[1], reverse=True))
for fan in sorted_fandom.keys():
    print(f"{fan}: {sorted_fandom[fan]}")
print()

print("Longest fics read")
longest_fic = sorted(fic_data.copy(), key=lambda x: x['word_count'], reverse=True)
for fic in longest_fic:
    print(f"{fic['title']}: {fic['word_count']}")
print()

print("Top warnings")
warnings_count = {}
for fic in fic_data:
    for warn in fic['warnings']:
        if warn in warnings_count.keys():
            warnings_count[warn] += 1
        else:
            warnings_count[warn] = 1

sorted_warnings = dict(sorted(warnings_count.items(), key=lambda x: x[1], reverse=True))
for warn in sorted_warnings.keys():
    print(f"{warn}: {sorted_warnings[warn]}")
print()


