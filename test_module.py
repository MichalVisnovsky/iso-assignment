import unittest
import json
import server
import requests
import pytest


class Test(unittest.TestCase):
    def setUp(self):
        with open('data.json') as json_file:
            self.data_set = json.load(json_file)
        self.server = server.MatchCountry(self.data_set)
        self.api_url = "http://localhost/match_country"

    def test_NonAscii(self):
        self.assertEqual(server.transliterate_non_ascii("Slovaška"), "Slovaska")
        self.assertEqual(server.transliterate_non_ascii("España"), "Espana")

    def test_is_valid_country(self):
        self.assertTrue(self.server.is_valid_country("SI", "Slovenia"))
        self.assertTrue(self.server.is_valid_country("SI", "Slovenija"))
        self.assertTrue(self.server.is_valid_country("SI", "Slovenie"))
        self.assertTrue(self.server.is_valid_country("SI", "Sloveniya"))
        self.assertFalse(self.server.is_valid_country("SI", "Sloven"))
        self.assertFalse(self.server.is_valid_country("SI", "Sloveni"))
        self.assertFalse(self.server.is_valid_country("SI", "Slovakia"))

    def test_api(self):
        try:
            data = {"iso": "SI",
                    "countries": ["Slovenia", "Slovenija", "Slovenie", "Sloveniya", "Slovensko", "United States"]}
            response = requests.post(self.api_url, json=data)
        except requests.exceptions.ConnectionError:
            pytest.skip("Server not running")

        assert response.status_code == 200
        result = {'iso': 'SI', 'match_count': 4,
                  'countries': ['Slovenia', 'Slovenija', 'Slovenie', 'Sloveniya']}

        assert response.json() == result

    def test_api2(self):
        try:
            data = {"iso": "JPN",
                    "countries": ["Slovenia", "Japan", "Slovenie", "Hapon", "Slovensko", "United States"]}
            response = requests.post(self.api_url, json=data)
        except requests.exceptions.ConnectionError:
            pytest.skip("Server not running")

        assert response.status_code == 200
        result = {'iso': 'JPN', 'match_count': 2,
                  'countries': ['Slovenia', 'Slovenija', 'Slovenie', 'Sloveniya']}

        assert response.json() != result

if __name__ == '__main__':
    unittest.main()
