import json
import os
from pytest import raises

import vcr
from asnake.aspace import ASpace
from asnake import utils

from .common import vcr


def load_fixture(filename, client=None):
    with open(os.path.join("tests/fixtures/utils", filename)) as json_file:
        data = json.load(json_file)
        return data


def test_get_note_text():
    """Checks whether the returned note text matches the selected query string."""
    for fixture, expected in [
            ("note_bibliography.json", [
                "bibliography", "item 1", "item 2"]),
            ("note_index.json", ["title1", "title2"]),
            ("note_multi.json", ["materials are restricted"]),
            ("note_multi_chronology.json", [
                "general note with chronology", "date", "event1", "event2"]),
            ("note_multi_defined.json", [
                "bioghist with defined list", "item", "1", "item", "2"]),
            ("note_multi_ordered.json", [
                "Bioghist with ordered list", "item1", "item2"]),
            ("note_single.json", ["Go Mets!"])]:
        note = load_fixture(fixture)
        result = utils.get_note_text(note)
        assert isinstance(result, list)
        assert set(result) == set(expected)


def test_text_in_note():
    """Checks whether the query string and note content are close to a match."""
    for fixture, query_string, expected in [
        ("note_single.json", "Go Mets!", True),
        ("note_single.json", "hello", False),
        ("note_multi.json", "materials are restricted", True),
        ("note_multi.json", "Boo Yankees", False)
    ]:
        note = load_fixture(fixture)
        result = utils.text_in_note(note, query_string)
        assert result == expected


@vcr.use_cassette
def test_object_locations():
    """Checks whether the function returns a list of dicts."""
    client = ASpace(baseurl="http://localhost:8089").client
    locations = utils.object_locations("/repositories/2/archival_objects/7", client)
    assert len(list(locations)) == 1
    for obj in locations:
        assert isinstance(obj, dict)


def test_format_resource_id():
    """Checks whether the function returns a concatenated string as expected."""
    for fixture, formatted, separator in [
            ("archival_object.json", "1;2;3;4", ";"),
            ("archival_object_2.json", "1:2:3", None)]:
        resource = load_fixture(fixture)
        if not separator:
            result = utils.format_resource_id(resource)
        else:
            result = utils.format_resource_id(resource, separator)
        assert isinstance(result, str)
        assert result == formatted


@vcr.use_cassette
def test_closest_value():
    client = ASpace().client
    value = utils.closest_value("/repositories/2/archival_objects/7", "extents", client)
    assert len(value) > 0


@vcr.use_cassette
def test_get_orphans():
    key = "linked_agents"
    client = ASpace().client
    archival_objects = [
        "/repositories/2/archival_objects/1",
        "/repositories/2/archival_objects/2",
        "/repositories/2/archival_objects/3",
        "/repositories/2/archival_objects/4",
        "/repositories/2/archival_objects/5",
        "/repositories/2/archival_objects/6",
        "/repositories/2/archival_objects/7"]
    orphans = utils.get_orphans(
        archival_objects, key, client)
    for o in orphans:
        assert isinstance(o, dict)
        assert o.get(key) in ["", [], {}, None]


def test_get_expression():
    """Tests whether the date expression function works as intended."""
    for fixture, expected in [
            ("date_expression.json", "1905-1980"),
            ("date_no_expression.json", "1905-1980"),
            ("date_no_expression_no_end.json", "1905")]:
        date = load_fixture(fixture)
        result = utils.get_expression(date)
        assert result == expected


def test_indicates_restriction():
    """Tests whether rights statements are correctly parsed for restrictions."""
    for fixture, restriction_acts, expected in [
            ("rights_statement_restricted.json",
             ["disallow", "conditional"], True),
            ("rights_statement_restricted.json", ["allow"], False),
            ("rights_statement_open.json",
             ["disallow", "conditional"], False),
            ("rights_statement_open.json", ["allow"], False),
            ("rights_statement_conditional.json",
             ["disallow", "conditional"], True),
            ("rights_statement_conditional.json", ["allow"], False),
            ("rights_statement_not_restricted.json",
             ["disallow", "conditional"], False),
            ("rights_statement_not_restricted.json", ["allow"], True)]:
        statement = load_fixture(fixture)
        status = utils.indicates_restriction(
            statement, restriction_acts)
        assert status == expected


def test_is_restricted():
    """Tests whether the function can find restrictions in an AS archival object."""
    for fixture, query_string, restriction_acts, expected in [
        ("archival_object.json", "materials are restricted",
         ["disallow", "conditional"], True),
        ("archival_object.json",
         "materials are restricted", ["allow"], True),
        ("archival_object.json", "test", ["allow"], False),
        ("archival_object_2.json", "materials are restricted",
         ["disallow", "conditional"], True),
        ("archival_object_2.json", "test", ["allow"], False),
        ("archival_object_3.json",
         "materials are restricted", ["allow"], False)
    ]:
        archival_object = load_fixture(fixture)
        result = utils.is_restricted(
            archival_object, query_string, restriction_acts)
        assert result == expected


def test_strip_html_tags():
    """Ensures HTML tags are correctly removed from strings."""
    input = "<h1>Title</h1><p>This is <i>some</i> text! It is wrapped in a variety of html tags, which should <strong>all</strong> be stripped &amp; not returned.</p>"
    expected = "TitleThis is some text! It is wrapped in a variety of html tags, which should all be stripped &amp; not returned."
    output = utils.strip_html_tags(input)
    assert output == expected


def test_format_from_obj():
    """Test that format strings can be passed to objects as expected."""
    for fixture, format_string in [
        ("date_expression.json", "{begin} - {end} ({expression})"),
        ("date_expression.json", None),
    ]:
        date = load_fixture(fixture)
        if not format_string:
            with raises(Exception) as excpt:
                utils.format_from_obj(date, format_string)
            assert str(excpt.value) == "No format string provided."
        else:
            formatted = utils.format_from_obj(
                date, format_string)
            assert formatted == "1905 - 1980 (1905-1980)"
            with raises(KeyError) as excpt:
                formatted = utils.format_from_obj(
                    date, "{start} - {end} ({expression})")
            assert "was not found in this object" in str(excpt.value)
