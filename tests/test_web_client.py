from .common import vcr
from asnake import ASnakeClient
import os

conf_file = None

def setup():
    '''Point ASNAKE_CONFIG_FILE at non-extant path so local config DEF HAPPENS even if you have a config'''
    try:
        conf_file = os.environ.pop('ASNAKE_CONFIG_FILE')
    except: pass
    os.environ['ASNAKE_CONFIG_FILE'] = "NONSENSEFILETHATDOESNOTEXIST"

@vcr.use_cassette
def test_authorize():
    client = ASnakeClient() # relies on default config, see ASnakeConfig class
    toke = client.authorize()
    assert isinstance(toke, str)
    assert len(toke) == 64
    assert set(toke) <= set('0123456789abcdef')
    assert client.session.headers['X-ArchivesSpace-Session'] == toke
    # Try to get admin user info, should only work if we're authed as admin
    assert client.get('users/1').status_code == 200

def teardown():
    '''Undo the thing from setup'''
    if conf_file:
        os.environ['ASNAKE_CONFIG_FILE'] = conf_file
    else:
        os.environ.pop('ASNAKE_CONFIG_FILE')
