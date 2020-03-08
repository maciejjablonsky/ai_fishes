from unittest import TestCase
import json

class Test(TestCase):
    def test_game_from_json(self):
        with open("fishes/resources/config.json", "r") as config_json:
            config = json.load(config_json)
            self.assertEqual(config['fishes']['number_of_fishes'], 50)
        
