import json
import os
from pytest import raises

import vcr
from asnake.aspace import ASpace
from asnake.jsonmodel import wrap_json_object
from asnake import utils

from .common import vcr


def load_fixture(filename, client=None):
    with open(os.path.join("tests/fixtures/utils", filename)) as json_file:
        data = json.load(json_file)
        return data


def test_resolve_to_uri():
    expected = "/repositories/2/archival_objects/1"
    for to_resolve in [
            expected,
            {"ref": expected},
            {"uri": expected},
            wrap_json_object({"uri": expected})]:
        resolved = utils.resolve_to_uri(to_resolve)
        assert resolved == expected


@vcr.use_cassette
def test_resolve_to_json():
    client = ASpace().client
    expected = load_fixture("archival_object.json")
    uri = "/repositories/2/archival_objects/1"
    for to_resolve in [
            uri,
            wrap_json_object(expected)]:
        resolved = utils.resolve_to_json(to_resolve, client)
        assert resolved == expected


@vcr.use_cassette
def test_get_note_text():
    """Checks whether the returned note text matches the selected query string."""
    client = ASpace().client
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
        result = utils.get_note_text(note, client)
        assert isinstance(result, list)
        assert set(result) == set(expected)


@vcr.use_cassette
def test_text_in_note():
    """Checks whether the query string and note content are close to a match."""
    client = ASpace().client
    for fixture, query_string, expected in [
        ("note_single.json", "Go Mets!", True),
        ("note_single.json", "hello", False),
        ("note_multi.json", "materials are restricted", True),
        ("note_multi.json", "Boo Yankees", False)
    ]:
        note = load_fixture(fixture)
        result = utils.text_in_note(note, query_string, client)
        assert result == expected


@vcr.use_cassette
def test_object_locations():
    """Checks whether the function returns a list of dicts."""
    client = ASpace().client
    locations = utils.get_object_locations("/repositories/2/archival_objects/7", client)
    assert len(list(locations)) == 1
    for obj in locations:
        assert isinstance(obj, dict)


@vcr.use_cassette
def test_format_resource_id():
    """Checks whether the function returns a concatenated string as expected."""
    client = ASpace().client
    for fixture, formatted, separator in [
            ("resource.json", "1;2;3;4", ";"),
            ("resource_2.json", "1:2:3", None)]:
        resource = load_fixture(fixture)
        if not separator:
            result = utils.format_resource_id(resource, client)
        else:
            result = utils.format_resource_id(resource, client, separator)
        assert isinstance(result, str)
        assert result == formatted


@vcr.use_cassette
def test_find_closest_value():
    client = ASpace().client
    value = utils.find_closest_value("/repositories/2/archival_objects/7", "extents", client)
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


@vcr.use_cassette
def test_get_date_display():
    """Tests whether the date display function works as intended."""
    client = ASpace().client
    for fixture, expected in [
            ("date_expression.json", "1905-1980"),
            ("date_no_expression.json", "1905-1980"),
            ("date_no_expression_no_end.json", "1905")]:
        date = load_fixture(fixture)
        result = utils.get_date_display(date, client)
        assert result == expected


@vcr.use_cassette
def test_indicates_restriction():
    """Tests whether rights statements are correctly parsed for restrictions."""
    client = ASpace().client
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
            statement, restriction_acts, client)
        assert status == expected


@vcr.use_cassette
def test_is_restricted():
    """Tests whether the function can find restrictions."""
    client = ASpace().client
    for fixture, query_string, restriction_acts, expected in [
        ("resource.json", "materials are restricted",
         ["disallow", "conditional"], True),
        ("resource.json", "materials are restricted",
         ["allow"], True),
        ("resource.json", "test", ["allow"], False),
        ("resource_2.json", "materials are restricted",
         ["disallow", "conditional"], True),
        ("resource_2.json", "test", ["allow"], False),
        ("resource_3.json", "materials are restricted",
         ["allow"], False)
    ]:
        archival_object = load_fixture(fixture)
        result = utils.is_restricted(
            archival_object, query_string, restriction_acts, client)
        assert result == expected


def test_strip_html_tags():
    """Ensures HTML tags are correctly removed from strings."""
    input = "<h1>Title</h1><p>This is <i>some</i> text! It is wrapped in a variety of html tags, which should <strong>all</strong> be stripped &amp; not returned.</p>"
    expected = "TitleThis is some text! It is wrapped in a variety of html tags, which should all be stripped &amp; not returned."
    output = utils.strip_html_tags(input)
    assert output == expected


@vcr.use_cassette
def test_format_from_obj():
    """Test that format strings can be passed to objects as expected."""
    client = ASpace().client
    for fixture, format_string in [
        ("date_expression.json", "{begin} - {end} ({expression})"),
        ("date_expression.json", None),
    ]:
        date = load_fixture(fixture)
        if not format_string:
            with raises(Exception) as excpt:
                utils.format_from_obj(date, format_string, client)
            assert str(excpt.value) == "No format string provided."
        else:
            formatted = utils.format_from_obj(
                date, format_string, client)
            assert formatted == "1905 - 1980 (1905-1980)"
            with raises(KeyError) as excpt:
                formatted = utils.format_from_obj(
                    date, "{start} - {end} ({expression})", client)
            assert "was not found in this object" in str(excpt.value)
