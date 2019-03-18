# ArchivesSnake
A client library for working with the ArchivesSpace API

## Purpose
As institutions have adopted ArchivesSpace, a variety of practitioners and institutions have written scripts making use of
the backend API to accomplish various bulk tasks not supported (yet) by the interface.  ArchivesSnake is intended to be
a comprehensive client library, to reduce duplication of effort and simplify scripting ArchivesSpace.

## Detailed API Doc
When you've read through this, please check out [the detailed API Docs](https://archivesspace-labs.github.io/ArchivesSnake/).  The
most important classes to understand are:

- asnake.aspace.ASpace
- asnake.client.ASnakeClient
- asnake.jsonmodel.JSONModelObject (and its subclasses ComponentObject and TreeNode)
- asnake.jsonmodel.JSONModelRelation

## Scripts and Projects using ASnake
Here are some examples scripts and projects that make use of ASnake

* [Python scripts to support ongoing ArchivesSpace work at Harvard](https://github.com/harvard-library/aspace_pyscripts)
* [GUI container location updater](https://gitlab.com/macasaurusrex/lsf)
* [API gateway for microservices](https://github.com/RockefellerArchiveCenter/zodiac)
* [ASpaceASnake](https://github.com/ruthtillman/ASpaceASnake)
* [ArchivesSpace scripts for University of Maryland Special Collections and University Archives](https://github.com/brialparker/ArchivesSpace_scripts)
* [Reporting and cleanup scripts for Rice University's Woodson Special Collections](https://github.com/scottythered/ASpace-Reporting-Cleanup)

For more examples on working with ASnake, please check the [Wiki page](https://github.com/archivesspace-labs/ArchivesSnake/wiki).

## Other API Scripts
Here are listed several examples of non-ASnake scripts that operate on ArchivesSpace - please feel free to submit your
own via pull request!

* [University of Denver links](Denver_links.md)
* [Duke Examples](Duke_links.md)
* [Harvard/Smith Ingest Client/Scripts](HarvardSmithLinks.md)
* [Johns Hopkins University links](Johns_Hopkins_University_links.md)
* [Penn State University Links](PSU_links.md)
* [RAC Examples](RAC_links.md)
* [Smith archivesspace Python Module](https://smithcollegelibraries.github.io/archivesspace-python/)
* [Outline of UAlbany Draft Library](ualbanyExample.md)
* [Yale University Links](Yale_Links.md)

## Requirements
ArchivesSnake has the following requirements.

- Python 3.4 or higher
- ability to install packages via pip ([Pipenv](https://docs.pipenv.org/) is recommended for development)

## Installation
ArchivesSnake is available from pypi:

``` bash
pip3 install ArchivesSnake
```

If you want to install from git:

``` bash
git clone https://github.com/archivesspace-labs/ArchivesSnake.git
cd ArchivesSnake
python3 setup.py sdist
pip3 install dist/ArchivesSnake-0.2.0.tar.gz
```

This is assuming a standard Python 3 install, which provides `pip3` and `python3` commands.  If your environment doesn't let you successfully run either command, please consult the documentation for your version of Python and/or your operating system.

You'll need an internet connection to fetch ASnake's dependencies.

## Usage
### Low level API
The low level API allows full access to the ArchivesSpace API; it's essentially "what if requests knew enough about an ASpace instance to manage authorization, turn uris into full URLs, and handle paged resources.

To start, here's a simple, fairly complete example - fetching the JSON representation of all the repositories from an ArchivesSpace instance and saving it to a variable.

``` python
from asnake.client import ASnakeClient

client = ASnakeClient(baseurl="http://my.aspace.backend.url.edu:4567",
                      username="admin",
                      password="admin")
client.authorize()
repos = client.get("repositories").json()

# do what thou wilt with some repos
```

The return values from these methods are raw `requests.models.Response` objects - you have to call `.json()` on them to get the actual JSON object.

There's also a `get_paged method`, which handles index methods (`repositories`, `repositories/:id/resources`, etc) and returns JSON for each object in the collection.

``` python
for repo in client.get_paged('repositories'):
    print(repo['name'])
```

The `ASnakeClient` class is a convenience wrapper over the [requests](http://docs.python-requests.org/en/master/) module.  The additional functionality it provides is:
- handles configuration,
- handles and persists authorization across multiple requests
- prepends a baseurl to API paths.

The latter means that this:

``` python
client.get('repositories')
```

is equivalent to:

``` python
requests.get("http://my.aspace.backend.url.edu:4567/repositories")
```

In addition to saving typing, the result of this is that the url fragments used as identifiers in ArchivesSpace `ref` objects can often (always?) be passed directly to these methods, e.g.:

``` python
uri = client.get('repositories/2').json()['agent_representation']['ref']
client.get(uri) # gets the agent!
```


### Abstraction Layer

The other way to use ASnake right now is a higher level, more convenient abstraction over the whole API.  It lets you ignore some of the low level details of the API, though you still need to know its structure.

There are three base classes involved: an `ASpace` class that represents the instance of ArchivesSpace you're connecting to, a `JSONModelObject` class that represents individual objects, and a `JSONModelRelation` class that represents routes that return groups of objects. Both JSONModel classes have subtypes for representing various exceptional cases in the API.

To use it, import the `asnake.aspace.ASpace` class.

#### JSONModelObject

JSONModelObjects wrap a single ASpace JSONModel object.  Method calls on JSONModelObjects will return either the value stored in the object's JSON representation, or will try to make a call to the API to fetch a subsidiary route.

So, for a JSONModelObject named `obj` wrapping this JSON:

``` json
{
    "jsonmodel_type": "repository",
    "uri": "/repositories/2",
    "name": "International Repository of Pancakes",
    ...
}
```

`obj.name` would return `"International Repository of Pancakes"`, and `obj.resources` would return a JSONModelRelation of the route `/repositories/2/resources`

##### Trees

JSONModelObjects representing resource or classification trees or nodes within those trees have specialized representation; specifically, they support two specialized properties:

``` python
a_tree.record # this returns the JSONModel object pointed to by that tree or node

a_tree.walk # this returns a generator that returns the record, followed by all records in the tree below it

# Usage example: printing a resource and all its subsidiary objects
for record in a_tree.walk:
    print(record.uri)
```

#### JSONModelRelation

JSONModelRelation objects "wrap" an API route representing either a collection of objects or an intermediate route (a route such as `/agents` that has child routes but no direct results.  A JSONModelRelation can be iterated over like a list, like so:

``` python
for repo in aspace.repositories:
    # do stuff with repo which is a JSONModelObject
```

You can get a copy of the wrapped JSON by doing:

``` python
obj.json()
```

The `.json` method makes a _deep copy_ of the object; otherwise, changes to the returned JSON would also affect the values inside the `JSONModelObject`.  If you run into memory issues, and are sure that you're not going to reuse the object you retrieved the JSON from, you can use:

``` python
obj._json
```

Which is the original wrapped JSON as returned from the API.

If you know the id of a particular thing in the collection, you can also treat `JSONModelRelation` objects as functions and pass the ids to get that specific thing, like so.

``` python
aspace.repositories(101) # repository with id 101
```

If you need to pass parameters to a route, you can add them using the `with_params` method; here's an example using the `/repositories/:repo_id/search` route to find published resources within a repository:

``` python
repo = aspace.repositories(101)
for resource in repo.search.with_params(q="primary_type:resource", fq="publish:true"):
    # do things with published resources from repo 101
```

A short full example using ASnake to print the title for all finding aids in ArchivesSpace, for example:

``` python
from asnake.aspace import ASpace

aspace = ASpace()

for repo in aspace.repositories:
    for resource in repo.resources:
        print(resource.title)
```

Currently, the `ASpace` interface is effectively read-only; if you need to create or update records (or just do something we haven't implemented yet), you'll have to drop down to the low-level
interface - for convenience, the `ASnakeClient` used by an `ASpace` object is accessible like so:

``` python
aspace.client.get('/repositories/2/resources/1')
```

For example, if you were really excited about archival data, and wanted to add an interrobang (‽) to the end of every resource's title, you'd do:

``` python
for repo in aspace.repositories:
    for resource in repo.resources:
        res_json = resource.json()
        res_json['title'] = res_json['title'] + '‽'
        aspace.client.post(resource.uri, json=res_json)
```

## Configuration

As per the example above, you can configure the client object by passing it arguments during creation.

Allowed configuration values are:

| **Setting**     | **Description**                                                               | **Default Value**     |
|-----------------|-------------------------------------------------------------------------------|-----------------------|
| baseurl         | The location (including port if not on port 80) of your archivesspace backend | http://localhost:4567 |
| username        | Username for authorization                                                    | admin                 |
| password        | Password for authorization                                                    | admin                 |
| retry_with_auth | Whether to respond to 403 errors by trying to authorize and retrying          | True                  |
| logging_config  | Hash with various config values for the logging subsystem                     | **see below**         |

The logging config allows the following settings, none of which are present by default:

| **Setting**    | **Description**                                                           | **Notes**                          |
|----------------|---------------------------------------------------------------------------|------------------------------------|
| default_config | A default configuration to start from, see                                | [Logging](#logging) for more info  |
| stream         | stream to be printed to (e.g. sys.stdin, sys.stdout, an open file)        | cannot be combined with stream     |
| filename       | name of file to be printed to                                             | cannot be combined with filename   |
| filemode       | mode to apply to file, as per `open` ('w' for write, 'a' for append, etc) | only useful combined with filename |
| level          | level to log at (e.g. 'INFO', 'DEBUG', 'WARNING')                         |                                    |

You can also define a configuration file, formatted in the [YAML](http://yaml.org/) markup language.  By default, ASnake looks for a file called `.archivessnake.yml` in the home directory of the user running it.  If an environment variable `ASNAKE_CONFIG_FILE` is set, ASnake will treat it as a filename and search there.

An example configuration file:

``` yaml
baseurl: http://localhost:4567
username: admin
password: admin
retry_with_auth: false
logging_config:
    default_config: INFO_TO_STDERR
```

Default values corresponding to the admin account of an unaltered local development instance of ASpace are included as fallback values.

### Logging


ArchivesSnake uses [structlog](http://www.structlog.org/en/stable/) combined with the stdlib logging module to provide configurable logging with reasonable defaults.  By default, log level is INFO, logging's default formatting is suppressed, and the log entries are formatted as line-oriented JSON and sent to standard error.  As logging in ArchivesSnake is by default universally below INFO level, in general the log will be silent unless you change configuration.  All of this can be configured; if you want to capture all possible logging from ASnake, that configuration should happen prior to creating an `asnake.client.ASnakeClient` or `asnake.aspace.ASpace` object

``` python
from asnake.client import ASnakeClient
import asnake.logging as logging

logging.setup_logging(level='DEBUG') # logging takes several arguments, provides defaults, etc

# NOW it is safe to initialize any ASnake stuff
client = ASnakeClient()
```

There are a number of provided configurations, available in dict `asnake.logging.configurations` and exposed as toplevel constants in the module (e.g. `asnake.logging.DEBUG_TO_STDERR`, `asnake.logging.DEFAULT_CONFIG`).  Log level and the stream/filename to be printed to can be overriden by passing `level` and *either* the `stream` or `filename` arguments to `setup_logging`. Mode of a file can be controlled by passing `filemode`.

For example:

``` python
logging.setup_logging(filename="my_precious.log", filemode="a") # write to my_precious.log, appending if it already exists
logging.setup_logging(stream=sys.stdout, level="DEBUG") # log to stdout, showing all log entry levels
```

The provided configurations are:

| Configuration Names | Level | Output To           | Notes                    |
|---------------------|-------|---------------------|--------------------------|
| DEFAULT_CONFIG      | INFO  | sys.stderr          | Alias for INFO_TO_STDERR |
| INFO_TO_STDERR      | INFO  | sys.stderr          |                          |
| INFO_TO_STDOUT      | INFO  | sys.stdout          |                          |
| INFO_TO_FILE        | INFO  | ~/archivessnake.log |                          |
| DEBUG_TO_STDERR     | DEBUG | sys.stderr          |                          |
| DEBUG_TO_STDOUT     | DEBUG | sys.stdout          |                          |
| DEBUG_TO_FILE       | DEBUG | ~/archivessnake.log |                          |

By setting the `ASNAKE_LOG_CONFIG` environment variable to one of these names, you can set that config as the default.

To directly get ahold of a logger for use in your own application, you can call `asnake.logging.get_logger`. An example of using this to print your own logs to a file:

``` python
import asnake.logging as logging

logging.setup_logging(filename='my_cool_logfile.log')
logger = logging.get_logger("my_script_log")

# do stuff
logger.info("my_event_name", property1="a property", anything={"json": "serializable"})
# do more stuff
```

This will leave the following in `my_cool_logfile.log` (pretty-printed below, but all on one line in practice):

``` javascript
{ "property1": "a property",
  "anything": {"json": "serializable"},
  "event": "my_event_name",
  "logger": "my_script_log",
  "level": "info",
  "timestamp": "2018-07-18T00:06:49.636482Z"
}
```

## Documentation
Documentation is generated using [Sphinx](http://www.sphinx-doc.org/en/stable/index.html) with the [Read the Docs Theme](https://sphinx-rtd-theme.readthedocs.io/en/latest/), and is available [here](https://archivesspace-labs.github.io/ArchivesSnake)
