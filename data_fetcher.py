import requests
from bs4 import BeautifulSoup
import time
import json
import re


def load_countries():
    countries = [['A', 'C'], ['D', 'I'], ['J', 'P'], ['Q', 'Z']]
    base_url = "https://en.wikipedia.org/wiki/List_of_country_names_in_various_languages_({}%E2%80%93{})"
    ret = []
    for country in countries:
        ret.extend(parse_data(base_url.format(country[0], country[1])))

    # write dataset to json file
    if ret:
        with open('data.json', 'w') as outfile:
            json.dump(ret, outfile)
    return ret


def parse_data(url):
    response = requests.get(url)
    time.sleep(1)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table', {'class': 'wikitable'})
        ret = []
        if table:
            for row in table.find_all('tr'):
                columns = row.find_all('td')
                if columns:
                    data = [column.get_text(strip=True) for column in columns]
                    if len(data) == 1:
                        continue
                    data[1] = re.sub(r'\([^)]*\)', '', data[1])
                    data[1] = re.sub(r'\[[^)]*\]', '', data[1])
                    data[1] = re.sub(r'-(.*?)(?=,)', '', data[1])

                    data[1] = data[1].split(',')
                    data[1] = [x.lower() for x in data[1]]

                    # load data to json
                    ret.append({'name': data[0], 'countries': data[1]})
            return ret

        else:
            print("Table not found on the page.")
    else:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")
