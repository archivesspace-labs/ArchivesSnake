from .common import vcr
from asnake import ASnakeClient

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
