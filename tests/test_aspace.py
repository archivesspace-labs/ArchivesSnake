from .common import vcr
from asnake.aspace import ASpace
from asnake.jsonmodel import JSONModelObject, TreeNode, ComponentObject, JSONModelRelation, searchdoc_signifiers
import os

conf_file = None
aspace = None

def setup():
    global aspace, conf_file
    '''Point ASNAKE_CONFIG_FILE at non-extant path so local config DEF HAPPENS even if you have a config'''
    try:
        conf_file = os.environ.pop('ASNAKE_CONFIG_FILE')
    except: pass
    os.environ['ASNAKE_CONFIG_FILE'] = "NONSENSEFILETHATDOESNOTEXIST"
    aspace = ASpace()

@vcr.use_cassette
def test_fetch():
    assert isinstance(aspace.repositories, JSONModelRelation)
    resolved = list(aspace.repositories)
    assert resolved[0].jsonmodel_type == "repository"
    repo_id = resolved[0].uri.split("/")[-1]
    assert isinstance(aspace.repositories(repo_id), JSONModelObject)

@vcr.use_cassette
def test_ordered_records():
    getem = list(aspace.resources)[0].ordered_records.uris
    assert len(getem) > 0
    assert all(isinstance(x, JSONModelObject) for x in getem)

@vcr.use_cassette
def test_stays_ref_on_repr():
    agent = aspace.repositories(2).agent_representation
    assert(agent.is_ref)
    agent.__repr__()
    assert(agent.is_ref)

@vcr.use_cassette
def test_agent_subroute():
    corp_ent = aspace.agents.corporate_entities
    assert isinstance(corp_ent, JSONModelRelation)
    # raised prior due to subroutes getting AgentRelation type
    agent = aspace.agents.corporate_entities(1)

@vcr.use_cassette
def test_by_external_id():
    result = next(aspace.by_external_id('thingumie'))
    assert isinstance(result, JSONModelObject)

@vcr.use_cassette
def test_trees():
    resource_tree = aspace.repositories(2).resources(1).tree
    assert isinstance(resource_tree.children[0], TreeNode)
    records_via_walk = list(resource_tree.walk)
    assert aspace.repositories(2).resources(1).json() == records_via_walk[0].json()
    assert isinstance(records_via_walk[1], ComponentObject)
    subtree_walk = list(records_via_walk[1].tree.walk)
    assert records_via_walk[1].uri == subtree_walk[0].uri

@vcr.use_cassette
def test_with_params():
    list(aspace.repositories(2).search.with_params(q="primary_type:resource", fq="publish:true"))

@vcr.use_cassette
def test_solr_route():
    list(aspace.repositories(2).top_containers.search.with_params(q="barcode_field:1234"))

@vcr.use_cassette
def test_from_uri():
    repo = aspace.from_uri('/repositories/2')
    assert isinstance(repo, JSONModelObject)
    assert repo.uri == '/repositories/2'
    repo.name # just making sure a known present method works

@vcr.use_cassette
def test_users_route():
    for user in  aspace.users:
        assert isinstance(user.permissions, dict)

@vcr.use_cassette
def test_search_route_unwrapping():
    # Get first ao, just really care that it ends up Not Wrapped
    ao = next(iter(aspace.repositories(2).search.with_params(q="*:* and primary_type:archival_object")))
    assert set(ao.json().keys()).isdisjoint(searchdoc_signifiers)

def teardown():
    '''Undo the thing from setup'''
    if conf_file:
        os.environ['ASNAKE_CONFIG_FILE'] = conf_file
    else:
        os.environ.pop('ASNAKE_CONFIG_FILE')
