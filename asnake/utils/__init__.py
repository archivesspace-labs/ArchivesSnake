# This is a module for holding utility functions in ArchivesSnake
#
# Note: module under active development, should be considered a WIP
#       code here subject to change and relocation with no notice
from collections.abc import Mapping
from itertools import chain

def resolve_to_uri(thingit, client):
    uri = None
    # if object has .json(), replace with value of .json()
    if callable(getattr(thingit, 'json', None)):
        thingit = thingit.json()

    if isinstance(thingit, str):
        uri = thingit
    elif isinstance(thingit, Mapping):
        uri = thingit.get("uri", thingit.get("ref", None))

    if not uri:
        raise Exception('Could not resolve "{}" to a URI'.format(thingit))

    return uri

def object_locations(ao_thingit, client):
    '''Given any of:
- the URI for an archival object
- a dict with a key 'uri' or 'ref' containing said URI
- an object responding to .json() returning such a dict

and an :class:`asnake.client.ASnakeClient`, this method will return a
generator which yields the JSON representation of any locations associated
with the archival object.'''
    ao_uri = resolve_to_uri(ao_thingit)
    assert 'archival_object' in ao_uri

    resp = client.get(ao_uri, params={'resolve': ['top_container::container_locations']})
    if resp.status_code != 200:
        raise Exception("Unable to fetch archival object with resolved container locations")

    for instance in resp.json()['instances']:
        for container_loc in instance['sub_container']['top_container']['_resolved']['container_locations']:
            yield container_loc['_resolved']

def walk_tree(thingit, client):
    '''Given any of:
- the URI for a resource
- the URI for an archival object
- a Mapping containing such a URI under the key 'uri'

and an :class:`asnake.client.ASnakeClient`, this method will return a generator
which yields the JSON representation of each successive element in the resource's tree,
in order.'''
    uri = resolve_to_uri(thingit, client)

    params = {'offset': 0}
    if not 'archival_object' in uri:
        resource_uri = uri
    else:
        node_uri = uri
        params['node_uri']= node_uri
        if isinstance(thingit, Mapping) and 'resource' in thingit:
            resource_uri = thingit['resource']['ref']
        else:
            resource_uri = client.get(node_uri).json()['resource']['ref']
    waypoints_uri = "/".join([resource_uri, "tree/waypoint"])
    if 'node_uri' in params:
        starting_waypoint = client.get("/".join([resource_uri, "tree/node"]), params=params).json()
    else:
        starting_waypoint = client.get("/".join([resource_uri, "tree/root"]), params=params).json()
    yield from _handle_waypoint(waypoints_uri, starting_waypoint, client)

def _page_waypoint_children(waypoints_uri, waypoint, client):
    params = {}
    if not 'resources' in waypoint['uri']:
        params['parent_node'] = waypoint['uri']

    for i in range(waypoint['waypoints']):
        params['offset'] = i
        for wp in client.get(waypoints_uri, params=params).json():
            yield wp

def _handle_waypoint(waypoints_uri, waypoint, client):
    # yield the record itself
    yield client.get(waypoint['uri']).json()

    # resource, omit parent_node_param
    for wp in _page_waypoint_children(waypoints_uri, waypoint, client):
            yield from _handle_waypoint(waypoints_uri, wp, client)
