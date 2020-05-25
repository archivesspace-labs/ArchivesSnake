# This is a module for holding utility functions in ArchivesSnake
#
# Note: module under active development, should be considered a WIP
#       code here subject to change and relocation with no notice
from collections.abc import Mapping

def object_locations(ao_thingit, client):
    '''Given any of:
- the URI for an archival object
- a dict with a key 'uri' or 'ref' containing said URI
- an object responding to .json() returning such a dict

and an :class:`asnake.client.ASnakeClient`, this method will return a
generator which yields the JSON representation of any locations associated
with the archival object.
'''
    ao_uri = None
    # if object has .json(), replace with value of .json()
    if callable(getattr(ao_thingit, 'json', None)):
        ao_thingit = ao_thingit.json()

    if isinstance(ao_thingit, str):
        ao_uri = ao_thingit
    elif isinstance(ao_thingit, Mapping):
        ao_uri = ao_thingit.get("uri", ao_thingit.get("ref", None))

    if not ao_uri:
        raise Exception('Object passed could not be understood as an Archival Object or URI')

    resp = client.get(ao_uri, params={'resolve': ['top_container::container_locations']})
    if resp.status_code != 200:
        raise Exception("Unable to fetch archival object with resolved container locations")

    for instance in resp.json()['instances']:
        for container_loc in instance['sub_container']['top_container']['_resolved']['container_locations']:
            yield container_loc['_resolved']
