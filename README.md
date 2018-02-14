# ArchivesSnake
A client library for working with the ArchivesSpace API

## Purpose
As institutions have adopted ArchivesSpace, a variety of practitioners and institutions have written scripts making use of
the backend API to accomplish various bulk tasks not supported (yet) by the interface.  ArchivesSnake is intended to be
a comprehensive client library, to reduce duplication of effort and simplify scripting ArchivesSpace.

## Prior Art
Here are listed several examples of pre-ASnake scripts that operate on ArchivesSpace - please feel free to submit your
own via pull request!

* [Duke Examples](Duke_links.md)
* [Harvard/Smith Ingest Client/Scripts](HarvardSmithLinks.md)
* [Johns Hopkins University links](Johns_Hopkins_University_links.md)
* [RAC Examples](RAC_links.md)
* [Outline of UAlbany Draft Library](ualbanyExample.md)
* [Yale University Links](Yale_Links.md)

## Requirements
ArchivesSnake has the following requirements.

- Python 3.4 or higher
- ability to install packages via pip ([Pipenv](https://docs.pipenv.org/) is recommended for development)

## Installation
Very soon, ArchivesSnake should be registered with pypi, but currently, to install, follow these steps.

``` bash
git clone https://github.com/archivesspace-labs/ArchivesSnake.git
cd ArchivesSnake
python3 setup.py sdist
pip3 install dist/ArchivesSnake-0.1.tar.gz
```

Note that this assumes your install of Python has `python3` and `pip3` aliases, which it should, especially if installed in a virtualenv.

You'll need an internet connection to fetch ASnake's dependencies.

## Usage
To start, here's a simple, fairly complete example - fetching the JSON representation of all the repositories from an ArchivesSpace instance and saving it to a variable.

``` python
from asnake import ASnakeClient

client = ASnakeClient(baseurl="http://my.aspace.backend.url.edu:4567",
                      username="admin",
                      password="admin")
client.authorize()
repos = client.get("repositories").json()

# do what thou wilt with some repos
```

Right now, there's a single user-visible class that's useful, ASnakeClient, which is a convenience wrapper
over the [requests](http://docs.python-requests.org/en/master/) module that handles configuration, authentication to
ArchivesSpace, and prepends a baseurl to API paths.

So this:

``` python
requests.get("http://my.aspace.backend.url.edu:4567/repositories")
```

is equivalent to:

``` python
client.get('repositories')
```

In addition to saving typing, the result of this is that the url fragments used as identifiers in ArchivesSpace `ref` objects can often (always?) be passed directly to these methods.

## Configuration

As per the example above, you can configure the client object by passing it arguments during creation.

Allowed configuration values are:

| **Setting** | **Description**                                                               |
|-------------|-------------------------------------------------------------------------------|
| baseurl     | The location (including port if not on port 80) of your archivesspace backend |
| username    | Username for authorization                                                    |
| password    | Password for authorization                                                    |

You can also define a configuration file, formatted in the [YAML](http://yaml.org/) markup language.  By default, ASnake looks for a file called `.archivessnake.yml` in the home directory of the user running it.  If an environment variable `ASNAKE_CONFIG_FILE` is set, ASnake will treat it as a filename and search there.

An example configuration file:

``` yaml
baseurl: http://localhost:4567
username: admin
password: admin
```

Default values corresponding to the admin account of an unaltered local development instance of ASpace are included as fallback values.

### Logging

ArchivesSnake uses [structlog](http://www.structlog.org/en/stable/) combined with the stdlib logging module to provide configurable logging with reasonable defaults.  By default, log level is INFO, logging's default formatting is suppressed, and the log entries are formatted as line-oriented JSON and sent to standard error.  All of this can be adjusted by configuring the logging module prior to loading the asnake library or any of its submodules, like so:

``` python
import logging, structlog, sys

logging.basicConfig(level=logging.DEBUG, format="%(message)s", stream=sys.stdout)
structlog.configure(
    ... # structlog configuration is somewhat complex, see docs
)
import asnake
```

Due to complexities of configuring Python logging, if you want to configure one of these components (logging, structlog) you'll need to _completely_ configure it; configuration will entirely _replace_ the defaults, rather than being merged with them.

## Documentation
Documentation is generated using [Sphinx](http://www.sphinx-doc.org/en/stable/index.html) with the [Read the Docs Theme](https://sphinx-rtd-theme.readthedocs.io/en/latest/), and is available [here](https://archivesspace-labs.github.io/ArchivesSnake)
