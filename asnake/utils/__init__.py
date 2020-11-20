# This is a module for holding utility functions in ArchivesSnake
#
# Note: module under active development, should be considered a WIP
#       code here subject to change and relocation with no notice
from datetime import date
import re
from rapidfuzz import fuzz
from asnake.jsonmodel import JSONModelObject
from string import Formatter
from collections.abc import Mapping
from itertools import chain


def resolve_to_uri(thingit):
    """Given any of:
- the URI for an ArchivesSpace object
- a dict with a key 'uri' or 'ref' containing said URI
- an object responding to .json() returning such a dict

this method will return a string containing the URI for that resource.
    """
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


def resolve_to_json(thingit, client):
    """Given any of:
- the URI for an ArchivesSpace object
- an object responding to .json() returning such a dict

this method will return a JSON representation of that object.
"""
    json = None
    if isinstance(thingit, dict):
        json = thingit
    elif callable(getattr(thingit, 'json', None)):
        json = thingit.json()
    else:
        uri = resolve_to_uri(thingit)
        json = client.get(thingit).json()
    if not json:
        raise Exception('Could not resolve {} to JSON.'.format(thingit))
    return json


def get_note_text(note, client):
    """Parses note content from different note types.

    :param dict: an ArchivesSpace note.

    :returns: a list containing note content.
    :rtype: list
    """
    def parse_subnote(subnote, client):
        """Parses note content from subnotes.

        :param dict: an ArchivesSpace subnote.

        :returns: a list containing subnote content.
        :rtype: list
        """
        subnote = resolve_to_json(subnote, client)
        if subnote["jsonmodel_type"] in [
                "note_orderedlist", "note_index"]:
            content = subnote["items"]
        elif subnote["jsonmodel_type"] in ["note_chronology", "note_definedlist"]:
            content = []
            for k in subnote["items"]:
                for i in k:
                    content += k.get(i) if isinstance(k.get(i),
                                                      list) else [k.get(i)]
        else:
            content = subnote["content"] if isinstance(
                subnote["content"], list) else [subnote["content"]]
        return content

    note = resolve_to_json(note, client)
    if note["jsonmodel_type"] in ["note_singlepart", "note_langmaterial"]:
        content = note["content"]
    elif note["jsonmodel_type"] == "note_bibliography":
        data = []
        data += note["content"]
        data += note["items"]
        content = data
    elif note["jsonmodel_type"] == "note_index":
        data = []
        for item in note["items"]:
            data.append(item["value"])
        content = data
    else:
        subnote_content_list = [parse_subnote(sn, client) for sn in note["subnotes"]]
        content = [
            c for subnote_content in subnote_content_list for c in subnote_content]
    return content


def text_in_note(note, query_string, client, confidence=97):
    """Performs fuzzy searching against note text.

    :param dict note: an ArchivesSpace note.
    :param str query_string: a string to match against.
    :param int confidence: minimum confidence ratio to match against.

    :returns: True if a match is found for `query_string`, False if no match is
            found.
    :rtype: bool
    """
    note = resolve_to_json(note, client)
    note_content = get_note_text(note, client)
    ratio = fuzz.partial_ratio(
        " ".join([n.lower() for n in note_content]),
        query_string.lower(),
        score_cutoff=confidence)
    return bool(ratio)


def format_from_obj(obj, format_string, client):
    """Generates a human-readable string from an object.

    :param JSONModelObject or dict: an ArchivesSpace object.

    :returns: a string in the chosen format.
    :rtype: str
    """
    obj = resolve_to_json(obj, client)
    if not format_string:
        raise Exception("No format string provided.")
    else:
        try:
            d = {}
            matches = [i[1] for i in Formatter().parse(format_string) if i[1]]
            for m in matches:
                d.update({m: obj[m]})
            return format_string.format(**d)
        except KeyError as e:
            raise KeyError(
                "The field {} was not found in this object".format(str(e)))


def format_resource_id(resource, client, separator=":"):
    """Concatenates the four-part ID for a resource record.

    :param dict resource: an ArchivesSpace resource.
    :param str separator: a separator to insert between the id parts. Defaults
            to `:`.

    :returns: a concatenated four-part ID for the resource record.
    :rtype: str
    """
    resource = resolve_to_json(resource, client)
    resource_id = []
    for x in range(4):
        try:
            resource_id.append(resource["id_{0}".format(x)])
        except KeyError:
            break
    return separator.join(resource_id)


def find_closest_value(archival_object, key, client):
    """Finds the closest value matching a key.

    Starts with an archival object, and iterates up through its ancestors
    until it finds a match for a key that is not empty or null.

    :param JSONModelObject archival_object: the URI for an archival object, a
        dict with a key 'uri' or 'ref' containing said URI, or an object
        responding to .json() returning such a dict
    :param str key: the key to match against.

    :returns: The value of the key, which could be a str, list, or dict.
    :rtype: str, list, or key
    """
    ao_uri = resolve_to_uri(archival_object)
    archival_object = client.get(ao_uri, params={'resolve': ['ancestors']}).json()
    if archival_object.get(key) not in ["", [], {}, None]:
        return archival_object[key]
    else:
        for ancestor in archival_object.get("ancestors"):
            anc = ancestor.get("_resolved")
            if anc.get(key) not in ["", [], {}, None]:
                return anc[key]


def get_orphans(object_list, null_attribute, client):
    """Finds objects in a list which do not have a value in a specified field.

    :param list object_list: a list of URIs for an archival object, dicts with
        a key 'uri' or 'ref' containing said URI, or objects responding to
        .json() returning such a dict
    :param null_attribute: an attribute which must be empty or null.

    :yields: a list of ArchivesSpace objects.
    :yield type: dict
    """
    for obj in object_list:
        obj = resolve_to_json(obj, client)
        if obj.get(null_attribute) in ["", [], {}, None]:
            yield obj


def get_date_display(date, client):
    """Returns a date expression for a date object.

    Concatenates start and end dates if no date expression exists.

    :param dict date: an ArchivesSpace date

    :returns: date expression for the date object.
    :rtype: str
    """
    date = resolve_to_json(date, client)
    try:
        expression = date["expression"]
    except KeyError:
        if date.get("end"):
            expression = "{0}-{1}".format(date["begin"], date["end"])
        else:
            expression = date["begin"]
    return expression


def indicates_restriction(rights_statement, restriction_acts, client):
    """Parses a rights statement to determine if it indicates a restriction.

    :param dict rights_statement: an ArchivesSpace rights statement.

    :returns: True if rights statement indicates a restriction, False if not.
    :rtype: bool
    """
    rights_statement = resolve_to_json(rights_statement, client)
    if is_expired(rights_statement.get("end_date")):
        return False
    for act in rights_statement.get("acts"):
        if (act.get("restriction")
                in restriction_acts and not is_expired(act.get("end_date"))):
            return True
    return False


def is_expired(date_str):
    """Takes a date and then checks whether today's date is before or after passed date.
    Will return a ValueError if passed date argument is an invalid date.

    :param string date: an ISO-formatted representation of a date

    :returns: False if date argument is after today or True if
    :rtype: bool
    """
    parsed_date = date.fromisoformat(date_str)
    return parsed_date < date.today()


def is_restricted(archival_object, query_string, restriction_acts, client):
    """Parses an archival object to determine if it is restricted.

    Iterates through notes, looking for a conditions governing access note
    which contains a particular set of strings.
    Also looks for associated rights statements which indicate object may be
    restricted.

    :param dict archival_object: an ArchivesSpace archival_object.
    :param list restriction_acts: a list of strings to match restriction act against.

    :returns: True if archival object is restricted, False if not.
    :rtype: bool
    """
    archival_object = resolve_to_json(archival_object, client)
    for note in archival_object["notes"]:
        if note["type"] == "accessrestrict":
            if text_in_note(note, query_string.lower(), client):
                return True
    for rights_statement in archival_object["rights_statements"]:
        if indicates_restriction(rights_statement, restriction_acts, client):
            return True
    return False


def strip_html_tags(string):
    """Strips HTML tags from a string.

    :param str string: An input string from which to remove HTML tags.
    """
    tag_match = re.compile("<.*?>")
    cleantext = re.sub(tag_match, "", string)
    return cleantext


def get_object_locations(ao_uri, client):
    """Given any of:
- the URI for an archival object
- a dict with a key 'uri' or 'ref' containing said URI
- an object responding to .json() returning such a dict

and an :class:`asnake.client.ASnakeClient`, this method will return a
generator which yields the JSON representation of any locations associated
with the archival object.
"""
    ao_uri = resolve_to_uri(ao_uri)
    resp = client.get(ao_uri, params={'resolve': ['top_container::container_locations']})

    if resp.status_code != 200:
        raise Exception("Unable to fetch archival object with resolved container locations")
    for instance in resp.json()['instances']:
        for container_loc in instance['sub_container']['top_container']['_resolved']['container_locations']:
            yield container_loc['_resolved']

def walk_tree(thingit, client):
    """Given any of:
- the URI for a resource
- the URI for an archival object
- a Mapping containing such a URI under the key 'uri'

and an :class:`asnake.client.ASnakeClient`, this method will return a generator
which yields the JSON representation of each successive element in the resource's tree,
in order."""
    uri = resolve_to_uri(thingit)

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
