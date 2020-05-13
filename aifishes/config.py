import json

config = None

def get_config(path='configuration.json'):
    global config
    if config is None:
        with open(path) as config_file:
            config = json.load(config_file)
    return config

def borders():
    return get_config()['environment']['dim']

def velocity_start_magnitude():
    return get_config()['fish']['velocity_start_magnitude']

def velocity_max_magnitude():
    return get_config()['fish']['velociy_max_magnitude']

def fish_dim():
    return get_config()['fish']['dim']

def fish_amount():
    return get_config()['fish']['amount']

def predator_dim():
    return get_config()['predator']['dim']

def predator_amount():
    return get_config()['predator']['amount']
