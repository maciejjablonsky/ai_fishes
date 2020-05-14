import json

config = None

def get_config(path='aifishes/configuration.json'):
    global config
    if config is None:
        with open(path) as config_file:
            config = json.load(config_file)
    return config

def borders():
    return get_config()['environment']['dim']

def fish_vel_start_magnitude():
    return get_config()['fish']['velocity']['start']

def fish_vel_max_magnitude():
    return get_config()['fish']['velocity']['max']

def fish_dim():
    return get_config()['fish']['dim']

def fish_amount():
    return get_config()['fish']['amount']

def predator_dim():
    return get_config()['predator']['dim']

def predator_amount():
    return get_config()['predator']['amount']

def predator_vel_start_magnitude():
    return get_config()['predator']['velocity']['start']

def predator_vel_max_magnitude():
    return get_config()['predator']['velocity']['max']

def fish():
    return get_config()['fish']

def predator():
    return get_config()['predator']