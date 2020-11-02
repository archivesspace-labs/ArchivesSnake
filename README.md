# ArchivesSnake
A client library for working with the ArchivesSpace API. As institutions have adopted ArchivesSpace, a variety of practitioners and institutions have written scripts making use of the backend API to accomplish various bulk tasks not yet supported by the interface. ArchivesSnake is intended to be a comprehensive client library, to reduce duplication of effort, and to simplify scripting in working with ArchivesSpace.

## To Use

### Requirements
ArchivesSnake has the following requirements:

- Python 3.4 or higher
- Ability to install packages via pip ([Pipenv](https://pypi.org/project/pipenv/) is recommended for development)

### Installation
For an overview of setup and configuration, see the [Getting Started Guide on the Wiki](https://github.com/archivesspace-labs/ArchivesSnake/wiki/Getting-Started-Guide).

ArchivesSnake is available from pypi:

``` bash
pip3 install ArchivesSnake
```

To install from git:

``` bash
git clone https://github.com/archivesspace-labs/ArchivesSnake.git
cd ArchivesSnake
python3 setup.py sdist
pip3 install dist/ArchivesSnake-0.9.0.tar.gz
```

This assumes a standard Python 3 install, which provides `pip3` and `python3` commands. If your environment doesn't allow you to successfully run either command, please consult the documentation for your version of Python and/or your operating system.

You'll need an internet connection to fetch ASnake's dependencies.

### Configuration

ArchivesSnake looks for a .archivessnake.yml file in the home directory.

* For OS X and Linux: `/home/[my user name]/.archivessnake.yml`
* For Windows: `C:\Users\[my user name]\.archivessnake.yml` 


An minimal example of a .archivessnake.yml file:

```yaml
baseurl: 'http://localhost:8089'
username: 'admin'
password: 'admin'
```

| **Setting**           | **Description**                                                               | **Default Value**       |
|-----------------------|-------------------------------------------------------------------------------|-------------------------|
| `baseurl`             | The location (including port if not on port 80) of your archivesspace backend | http://localhost:4567   |
| `username`            | Username for authorization                                                    | admin                   |
| `password`            | Password for authorization                                                    | admin                   |
| `session_token`       | Session token for authorization                                               | **see below**           |
| `session_header_name` | Header to send session token in                                               | X-ArchivesSpace-Session |
| `retry_with_auth`     | Whether to respond to 403 errors by trying to authorize and retrying          | True                    |
| `logging_config`      | Hash with various config values for the logging subsystem                     | **see below**           |

`username`/`password` and `session_token` are mutually exclusive. In a normally configured ArchivesSpace system, you will want to use `username`/`password`. `session_token` allows you to set a fixed value for the session, in case you are sharing a long-lived session amongst several apps, or using an authorization customization that bypasses the ArchivesSpace login route. Examples of this include proxies or SSO plugins.  `session_header_name` lets you customize the header you pass the session in, since some proxies use a different header than `X-ArchivesSpace-Session`.

The logging config allows the following settings, none of which are present by default:

| **Setting**      | **Description**                                                           | **Notes**                             |
|------------------|---------------------------------------------------------------------------|---------------------------------------|
| `default_config` | A default configuration to start from                                     | See [logging](#logging) for more info |
| `stream`         | stream to be printed to (e.g. sys.stdin, sys.stdout, an open file)        | Cannot be combined with `filename`    |
| `filename`       | name of file to be printed to                                             | Cannot be combined with `stream`      |
| `filemode`       | mode to apply to file, as per `open` ('w' for write, 'a' for append, etc) | Only useful combined with `filename`  |
| `level`          | level to log at (e.g. 'INFO', 'DEBUG', 'WARNING')                         |                                       |

You can also define a configuration file, formatted in the [YAML markup language](http://yaml.org/). By default, ASnake looks for a file called `.archivessnake.yml` in the home directory of the user running it.  If an environment variable `ASNAKE_CONFIG_FILE` is set, ASnake will treat it as a filename and search there.

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
ArchivesSnake uses [structlog](http://www.structlog.org/en/stable/) combined with the stdlib logging module to provide configurable logging with reasonable defaults. By default, log level is INFO, logging's default formatting is suppressed, and the log entries are formatted as line-oriented JSON and sent to standard error. Logging in ArchivesSnake is by default universally below INFO level, so in general the log will be silent unless you change the configuration. All of this can be configured; if you want to capture all possible logging from ASnake, that configuration should happen prior to creating an `asnake.client.ASnakeClient` or `asnake.aspace.ASpace` object:

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

To directly get ahold of a logger for use in your own application, you can call `asnake.logging.get_logger`. For example, to print your own logs to a file:

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
## Functionality

### Low-level API
The low-level API allows full access to the ArchivesSpace API unlike the ArchivesSnake [Abstraction Layer](#Abstraction_Layer) which is effectively “read-only." The ArchivesSnake client operates as a wrapper over the Python requests module which allows users to send HTTP requests using Python. The low-level API client manages authorization, turns uris into full URLs, and handles paged resources. For further examples see use cases in the Wiki.

For example, to fetch the JSON representation of all the repositories from an ArchivesSpace instance and save it to a variable:

``` python
from asnake.client import ASnakeClient

client = ASnakeClient(baseurl="http://my.aspace.backend.url.edu:4567",
                      username="admin",
                      password="admin")
client.authorize()
repos = client.get("repositories").json()

# do what thou wilt with some repos
```

The return values from these methods are raw `requests.models.Response` objects. You have to call `.json()` on them to get the actual JSON object.

There's also a `get_paged method`, which handles index methods (`repositories`, `repositories/:id/resources`, etc) and returns JSON for each object in the collection.

``` python
for repo in client.get_paged('repositories'):
    print(repo['name'])
```

The `ASnakeClient` class is a convenience wrapper over the [requests](http://docs.python-requests.org/en/master/) module. It provides additional functionality to:
- Handle configuration
- Handle and persist authorization across multiple requests
- Prepend a baseurl to API paths

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
The other way to use ASnake right now is a higher level, more convenient abstraction over the whole API. It lets you ignore some of the low-level details of the API, though you still need to know its structure. To use it, import the `asnake.aspace.ASpace` class.

There are three base classes involved:
1. An `ASpace` class that represents the instance of ArchivesSpace you're connecting to
2. A `JSONModelObject` class that represents individual objects
3. A `JSONModelRelation` class that represents routes that return groups of objects. Both JSONModel classes have subtypes for representing various exceptional cases in the API.

#### JSONModelObject
JSONModelObjects wrap a single ASpace JSONModel object. Method calls on JSONModelObjects will return either the value stored in the object's JSON representation, or will try to make a call to the API to fetch a subsidiary route.

For a JSONModelObject named `obj` wrapping this JSON:

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
JSONModelObjects representing resource or classification trees, or nodes within those trees, have specialized representation. Specifically, they support two specialized properties:

``` python
a_tree.record # this returns the JSONModel object pointed to by that tree or node

a_tree.walk # this returns a generator that returns the record, followed by all records in the tree below it

#Usage example for printing a resource and all its subsidiary objects:
for record in a_tree.walk:
    print(record.uri)
```
#### JSONModelRelation
JSONModelRelation objects "wrap" an API route representing either a collection of objects or an intermediate route (a route such as `/agents` that has child routes but no direct results. A JSONModelRelation can be iterated over like a list:

``` python
for repo in aspace.repositories:
    # do stuff with repo which is a JSONModelObject
```

Get a copy of the wrapped JSON using:

``` python
obj.json()
```

The `.json` method makes a [deep copy](https://en.wikipedia.org/wiki/Object_copying#Deep_copy) of the object. This means that it creates a new collection object and then inserts copies of the objects found within the original object rather than just references to them. Otherwise, changes to the returned JSON would also affect the values inside the `JSONModelObject`. If you run into memory issues and are sure that you will not reuse the object from which you retrieved the JSON, you can use:

``` python
obj._json
```

This is the original wrapped JSON as returned from the API.

If you know the specific id of something in the collection, you can also treat `JSONModelRelation` objects as functions and pass the ids to retrieve that particular thing, like so:

``` python
aspace.repositories(101) # repository with id 101
```

If you need to pass parameters to a route, you can add them using the `with_params` method. An example using the `/repositories/:repo_id/search` route to find published resources within a repository:

``` python
repo = aspace.repositories(101)
for resource in repo.search.with_params(q="primary_type:resource AND publish:true"):
    # do things with published resources from repo 101
```

An example using ASnake to print the title for all finding aids in ArchivesSpace:

``` python
from asnake.aspace import ASpace

aspace = ASpace()

for repo in aspace.repositories:
    for resource in repo.resources:
        print(resource.title)
```

Currently, the `ASpace` interface is read-only. If you need to create or update records (or just do something that we haven't implemented yet), you'll have to drop down to the low-level interface. For convenience, the `ASnakeClient` used by an `ASpace object` is accessible using:

``` python
aspace.client.get('/repositories/2/resources/1')
```

For example, if you were really excited about archival data, and wanted to add an interrobang punctuation mark (‽) to the end of every resource's title:

``` python
for repo in aspace.repositories:
    for resource in repo.resources:
        res_json = resource.json()
        res_json['title'] = res_json['title'] + '‽'
        aspace.client.post(resource.uri, json=res_json)
```

## Detailed API Doc
[Detailed ASnake API documentation](https://archivesspace-labs.github.io/ArchivesSnake/) is generated from docstrings using [Sphinx](https://www.sphinx-doc.org/en/master/index.html) with the [Read the Docs Theme](https://sphinx-rtd-theme.readthedocs.io/en/latest/).

The most important classes to understand are:
- asnake.aspace.ASpace
- asnake.client.ASnakeClient
- asnake.jsonmodel.JSONModelObject (and its subclasses ComponentObject and TreeNode)
- asnake.jsonmodel.JSONModelRelation

## Scripts and Projects using ASnake
Here are some example scripts and projects that make use of ASnake:

* [Python scripts to support ongoing ArchivesSpace work at Harvard](https://github.com/harvard-library/aspace_pyscripts)
* [Python scripts to support container and instance data migration, also at Harvard](https://github.com/harvard-library/aspace_container_mgmt_scripts)
* [GUI container location updater](https://gitlab.com/macasaurusrex/lsf)
* [API gateway for microservices](https://github.com/RockefellerArchiveCenter/zodiac)
* [ASpaceASnake](https://github.com/ruthtillman/ASpaceASnake)
* [ArchivesSpace scripts for University of Maryland Special Collections and University Archives](https://github.com/brialparker/ArchivesSpace_scripts)
* [Reporting and cleanup scripts for Rice University's Woodson Special Collections](https://github.com/scottythered/ASpace-Reporting-Cleanup)
* [CLI tool for downloading resources to local JSON files](https://github.com/jakekara/archives-space-scraper)

For more examples on working with ASnake, please check the [Wiki page](https://github.com/archivesspace-labs/ArchivesSnake/wiki).

## Other API Scripts
The [`other_API_scripts`](/other_API_scripts) directory contains several examples of non-ASnake scripts that operate on ArchivesSpace. Please feel free to submit your own via pull request!

## Contributing
ArchivesSnake is a community driven, open source project. Contributions are welcome, and all contributors will be acknowledged. All contributions made to ArchivesSnake must be available for distribution under an Apache 2.0 License.

Overview of how to contribute:

1. File an issue in the repository or work on an issue already documented
2. Fork the repository and create a new branch for your work
3. After you have completed your work, push your branch back to the repository and open a pull request

Pull requests will be reviewed and merged by the ArchivesSnake Developer Team.

## License
Copyright 2018 ArchivesSnake Developer Team. Licensed under the [Apache License Version 2.0](http://www.apache.org/licenses/LICENSE-2.0). See [LICENSE.txt](https://github.com/archivesspace-labs/ArchivesSnake/blob/master/LICENSE.txt) for more details.
