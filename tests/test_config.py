from asnake import ASnakeConfig
import os
from os.path import dirname, join

def setup():
    os.environ['ASNAKE_CONFIG_FILE'] = join(dirname(__file__), 'fixtures', 'asnake.yml')

def test_config_from_file():
    expected = {
        "username": "APIUser",
        "password": "APIPass",
        "baseurl":  "http://notarealurl.com:4567"
    }

    config = ASnakeConfig()
    for k in expected:
        assert expected[k] == config[k]


def test_direct_config():
    expected = {
        "username": "directUser",
        "password": "directPass",
        "baseurl": "directNotRealUrl"
    }

    config = ASnakeConfig()
    config.update(expected)
    for k in expected:
        assert expected[k] == config[k]


def teardown():
    os.environ.pop('ASNAKE_CONFIG_FILE')
