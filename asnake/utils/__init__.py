# This is a module for holding utility functions in ArchivesSnake
#
# Note: module under active development, should be considered a WIP
#       code here subject to change and relocation with no notice
from collections.abc import Mapping
from datetime import datetime
import re
from rapidfuzz import fuzz
from asnake.jsonmodel import JSONModelObject
from string import Formatter

from .decorators import check_type


@check_type(dict)
def get_note_text(note):
    """Parses note content from different note types.

    :param dict: an ArchivesSpace note.

    :returns: a list containing note content.
    :rtype: list
    """
    def parse_subnote(subnote):
        """Parses note content from subnotes.

        :param dict: an ArchivesSpace subnote.

        :returns: a list containing subnote content.
        :rtype: list
        """
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

    if note["jsonmodel_type"] == "note_singlepart":
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
        subnote_content_list = list(parse_subnote(sn)
                                    for sn in note["subnotes"])
        content = [
            c for subnote_content in subnote_content_list for c in subnote_content]
    return content


@check_type(dict)
def text_in_note(note, query_string):
    """Performs fuzzy searching against note text.

    :param dict note: an ArchivesSpace note.
    :param str query_string: a string to match against.

    :returns: True if a match is found for `query_string`, False if no match is
            found.
    :rtype: bool
    """
    CONFIDENCE_RATIO = 97
    """int: Minimum confidence ratio to match against."""
    note_content = get_note_text(note)
    ratio = fuzz.token_sort_ratio(
        " ".join([n.lower() for n in note_content]),
        query_string.lower(),
        score_cutoff=CONFIDENCE_RATIO)
    return bool(ratio)


@check_type(JSONModelObject)
def format_from_obj(obj, format_string):
    """Generates a human-readable string from an object.

    :param JSONModelObject location: an ArchivesSpace object.

    :returns: a string in the chosen format.
    :rtype: str
    """
    if not format_string:
        raise Exception("No format string provided.")
    else:
        try:
            d = {}
            matches = [i[1] for i in Formatter().parse(format_string) if i[1]]
            for m in matches:
                d.update({m: getattr(obj, m, "")})
            return format_string.format(**d)
        except KeyError as e:
            raise KeyError(
                "The field {} was not found in this object".format(
                    str(e)))


@check_type(dict)
def format_resource_id(resource, separator=":"):
    """Concatenates the four-part ID for a resource record.

    :param dict resource: an ArchivesSpace resource.
    :param str separator: a separator to insert between the id parts. Defaults
            to `:`.

    :returns: a concatenated four-part ID for the resource record.
    :rtype: str
    """
    resource_id = []
    for x in range(4):
        try:
            resource_id.append(resource["id_{0}".format(x)])
        except KeyError:
            break
    return separator.join(resource_id)


@check_type(JSONModelObject)
def closest_value(archival_object, key):
    """Finds the closest value matching a key.

    Starts with an archival object, and iterates up through its ancestors
    until it finds a match for a key that is not empty or null.

    :param JSONModelObject archival_object: an ArchivesSpace archival_object.
    :param str key: the key to match against.

    :returns: The value of the key, which could be a str, list, or dict.
    :rtype: str, list, or key
    """
    if getattr(archival_object, key) not in ["", [], {}, None]:
        return getattr(archival_object, key)
    else:
        for ancestor in archival_object.ancestors:
            return closest_value(ancestor, key)


def get_orphans(object_list, null_attribute):
    """Finds objects in a list which do not have a value in a specified field.

    :param list object_list: a list of ArchivesSpace objects.
    :param null_attribute: an attribute which must be empty or null.

    :yields: a list of ArchivesSpace objects.
    :yield type: dict
    """
    for obj in object_list:
        if getattr(obj, null_attribute) in ["", [], {}, None]:
            yield obj


@check_type(dict)
def get_expression(date):
    """Returns a date expression for a date object.

    Concatenates start and end dates if no date expression exists.

    :param dict date: an ArchivesSpace date

    :returns: date expression for the date object.
    :rtype: str
    """
    try:
        expression = date["expression"]
    except KeyError:
        if date.get("end"):
            expression = "{0}-{1}".format(date["begin"], date["end"])
        else:
            expression = date["begin"]
    return expression


@check_type(dict)
def indicates_restriction(rights_statement, restriction_acts):
    """Parses a rights statement to determine if it indicates a restriction.

    :param dict rights_statement: an ArchivesSpace rights statement.

    :returns: True if rights statement indicates a restriction, False if not.
    :rtype: bool
    """
    def is_expired(date):
        today = datetime.now()
        date = date if date else datetime.strftime("%Y-%m-%d")
        return False if (
            datetime.strptime(date, "%Y-%m-%d") >= today) else True

    if is_expired(rights_statement.get("end_date")):
        return False
    for act in rights_statement.get("acts"):
        if (act.get("restriction")
                in restriction_acts and not is_expired(act.get("end_date"))):
            return True
    return False


@check_type(dict)
def is_restricted(archival_object, query_string, restriction_acts):
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
    for note in archival_object["notes"]:
        if note["type"] == "accessrestrict":
            if text_in_note(note, query_string.lower()):
                return True
    for rights_statement in archival_object["rights_statements"]:
        if indicates_restriction(rights_statement, restriction_acts):
            return True
    return False


@check_type(str)
def strip_html_tags(string):
    """Strips HTML tags from a string.

    :param str string: An input string from which to remove HTML tags.
    """
    tag_match = re.compile("<.*?>")
    cleantext = re.sub(tag_match, "", string)
    return cleantext


def object_locations(ao_thingit, client):
    '''Given any of:
- the URI for an archival object
- a dict with a key 'uri' or 'ref' containing said URI
- an object responding to .json() returning such a dict

and an :class:`asnake.client.ASnakeClient`, this method will return a
generator which yields the JSON representation of any locations associated
with the archival object.
'''

    for instance in resp.json()['instances']:
        for container_loc in instance['sub_container']['top_container']['_resolved']['container_locations']:
            yield container_loc['_resolved']
