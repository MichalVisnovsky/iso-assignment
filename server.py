import sys

import bs4
import pycountry
import json
from unidecode import unidecode
from flask import Flask, request, jsonify
import data_fetcher

app = Flask(__name__)


def transliterate_non_ascii(text):
    # unidecode only ascii characters (chinese/arabic/etc. characters are skipped)
    return ''.join([unidecode(char) if ord(char) > 127 else char for char in text])


class MatchCountry:
    def __init__(self, data_set):
        self.data_set = data_set

    def is_valid_country(self, iso, country_name):
        name_iso = None

        # check if iso is valid
        if len(iso) == 2 or len(iso) == 3:
            if len(iso) == 2:
                name_iso = pycountry.countries.get(alpha_2=iso).name
            elif iso.isdigit():
                name_iso = pycountry.countries.get(numeric=iso).name
            else:
                name_iso = pycountry.countries.get(alpha_3=iso).name

        if not name_iso:
            return False

        # get row by iso
        data_row = [item for item in self.data_set if item['name'] == name_iso][0]['countries']
        # add transliterated ascii characters to the row
        data_row_ascii = [transliterate_non_ascii(item) for item in data_row]
        data_row.extend(data_row_ascii)

        # check if country_name is in the row
        if country_name.lower() in data_row or \
                transliterate_non_ascii(country_name.lower()) in data_row:
            return True
        else:
            return False


@app.route('/match_country', methods=['POST'])
def handle_post_request():
    try:
        # Get the JSON data from the POST request
        try:
            input_json = request.get_json(force=True)
        except Exception as e:
            # try to load it this way, when it fails (curl)
            input_json = json.loads(bs4.UnicodeDammit.detwingle(request.get_data()).decode('utf-8'))
        # Check all countries
        print(input_json, file=sys.stderr)
        matches = {'iso': input_json['iso'], 'match_count': 0, 'countries': []}
        for country in input_json['countries']:
            if match_country.is_valid_country(input_json["iso"].upper(), country):
                matches['match_count'] += 1
                matches['countries'].append(country)

        return jsonify(matches), 200  # Return a JSON response with a 200 OK status

    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == '__main__':

    # if data.json file exists, load data from it
    try:
        with open('data.json') as json_file:
            data = json.load(json_file)
    except FileNotFoundError:
        print("data.json file not found. Fetching...")
        data = data_fetcher.load_countries()

    # create object
    match_country = MatchCountry(data)

    # start server
    app.run(port=80)
