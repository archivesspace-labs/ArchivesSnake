from .common import vcr
from asnake.aspace import ASpace
from asnake.jsonmodel import JSONModelObject, TreeNode, ComponentObject, JSONModelRelation
import os

conf_file = None

def setup():
    '''Point ASNAKE_CONFIG_FILE at non-extant path so local config DEF HAPPENS even if you have a config'''
    try:
        conf_file = os.environ.pop('ASNAKE_CONFIG_FILE')
    except: pass
    os.environ['ASNAKE_CONFIG_FILE'] = "NONSENSEFILETHATDOESNOTEXIST"

@vcr.use_cassette
def test_fetch():
    aspace = ASpace()
    assert isinstance(aspace.repositories, JSONModelRelation)
    resolved = list(aspace.repositories)
    assert resolved[0].jsonmodel_type == "repository"
    repo_id = resolved[0].uri.split("/")[-1]
    assert isinstance(aspace.repositories(repo_id), JSONModelObject)

@vcr.use_cassette
def test_ordered_records():
    aspace = ASpace()
    getem = list(aspace.resources)[0].ordered_records.uris
    assert len(getem) > 0
    assert all(isinstance(x, JSONModelObject) for x in getem)

@vcr.use_cassette
def test_stays_ref_on_repr():
    aspace = ASpace()
    agent = aspace.repositories(2).agent_representation
    assert(agent.is_ref)
    agent.__repr__()
    assert(agent.is_ref)

@vcr.use_cassette
def test_agent_subroute():
    aspace = ASpace()
    corp_ent = aspace.agents.corporate_entities
    assert isinstance(corp_ent, JSONModelRelation)
    # raised prior due to subroutes getting AgentRelation type
    agent = aspace.agents.corporate_entities(1)

@vcr.use_cassette
def test_by_external_id():
    aspace = ASpace()
    result = next(aspace.by_external_id('thingumie'))
    assert isinstance(result, JSONModelObject)

@vcr.use_cassette
def test_trees():
    aspace = ASpace()
    resource_tree = aspace.repositories(2).resources(1).tree
    assert isinstance(resource_tree.children[0], TreeNode)
    records_via_walk = list(resource_tree.walk)
    assert aspace.repositories(2).resources(1).json() == records_via_walk[0].json()
    assert isinstance(records_via_walk[1], ComponentObject)
    subtree_walk = list(records_via_walk[1].tree.walk)
    assert records_via_walk[1].uri == subtree_walk[0].uri

def teardown():
    '''Undo the thing from setup'''
    if conf_file:
        os.environ['ASNAKE_CONFIG_FILE'] = conf_file
    else:
        os.environ.pop('ASNAKE_CONFIG_FILE')
