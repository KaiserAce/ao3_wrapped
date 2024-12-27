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
print(os.getenv("USER_NAME"), os.getenv("PASSWORD"))

payload = {
    "user[login]": os.getenv("USER_NAME"),
    "user[password]": os.getenv("PASSWORD"),
    "authenticity_token": token,
    "commit": "Log in",
}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Referer": login_url
}

login_response = session.post(login_url, data=payload, headers=headers)

if login_response.status_code == 200:
    print("Login attempt completed.")

    if "My Dashboard" in login_response.text:
        print("Login successful!")

        for i in range(1, 3):
            time.sleep(5)
            new_page_response = session.get(f'https://archiveofourown.org/users/Kaiser_Ace/readings?page={i}')
            if new_page_response.status_code == 200:
                print("Successfully accessed the new page.")

                page = BeautifulSoup(new_page_response.content, "html.parser")

                raw_data = page.find("ol", class_="reading work index group")
                raw_indiv_items = raw_data.find_all("li", role="article")
                for item in raw_indiv_items:
                    header = item.find("div", class_="header module")
                    heading = header.find("h4")
                    title = heading.find_all("a")[0].text
                    print(title)
            else:
                print("Page traversal failed")
                exit()


    else:
        print("Login failed. Check your credentials or the token.")
else:
    print(f"Login request failed with status code {login_response.status_code}")
