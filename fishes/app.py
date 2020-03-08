from fishes.game.game import game_from_json


def run():
    game = game_from_json()
    game.run()
